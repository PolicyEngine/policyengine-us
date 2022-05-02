import collections
from typing import Union
import numpy as np
import requests
from pathlib import Path
import pandas as pd
import subprocess
import stat
from io import StringIO
from openfisca_us.data.datasets.cps.cps import CPS
from openfisca_tools.data import Dataset
from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_us.api.microsimulation import Microsimulation
from tqdm import tqdm


class TaxSim35:
    EXECUTABLE_URL = "https://taxsim.nber.org/stata/taxsim35/taxsim35-unix.exe"
    folder = Path(__file__).parent.absolute()
    executable_path = folder / "taxsim35.exe"
    INPUT_VARIABLES = [
        "taxsimid",
        "year",
        "state",
        "mstat",
        "page",
        "sage",
        "depx",
        "age1",
        "age2",
        "age3",
        "dep13",
        "dep17",
        "dep18",
        "pwages",
        "swages",
        "psemp",
        "ssemp",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        # "otherprop",
        # "nonprop",
        "pensions",
        "gssi",
        "pui",
        "ui",
        # "transfers",
        # "rentpaid",
        # "proptax",
        # "otheritem",
        "childcare",
        # "mortgage",
        "scorp",
        # "pbusinc",
        # "pprofinc",
        # "sbusinc",
        # "sprofinc",
    ]
    UNIMPLEMENTED_VARIABLES = [
        "otherprop",
        "nonprop",
        "transfers",
        "rentpaid",
        "proptax",
        "otheritem",
        "mortgage",
        "pbusinc",
        "pprofinc",
        "sbusinc",
        "sprofinc",
    ]
    OUTPUT_VARIABLES = [
        "v10",
    ]
    OPENFISCA_US_INPUT_VARIABLES = [
        "mars",
        "employment_income",
        "age",
        "is_tax_unit_head",
        "is_tax_unit_spouse",
        "is_tax_unit_dependent",
        "self_employment_income",
        "dividend_income",
        "pension_income",
        "social_security",
        "unemployment_insurance",
        "tax_unit_childcare_expenses",
        "short_term_capital_gains",
        "long_term_capital_gains",
        "taxable_interest",
        "filer_partnership_s_corp_income",
        "tax_unit_id",
        "person_tax_unit_id",
    ]

    def __init__(self):
        self.ensure_executable_is_ready()

    @property
    def executable_is_stored(self):
        return (self.folder / "taxsim35.exe").exists()

    def ensure_executable_is_ready(self):
        if not self.executable_is_stored:
            # Download the .exe file and save to the folder
            response = requests.get(self.EXECUTABLE_URL)
            with open(self.folder / "taxsim35.exe", "wb") as f:
                f.write(response.content)
            self.executable_path.chmod(
                self.executable_path.stat().st_mode | stat.S_IEXEC
            )

    def calculate(self, input_data: dict) -> dict:
        if isinstance(input_data, pd.DataFrame):
            input_csv = input_data
        else:
            input_csv = pd.DataFrame(
                {
                    col: [value]
                    if not isinstance(value, collections.Sequence)
                    else value
                    for col, value in input_data.items()
                }
            )
        input_csv_text = input_csv.to_csv(index=False)
        # We would usually run: taxsim35.exe < input.csv > output.csv.
        # But we're in a Python interface, so we just want the output as a DataFrame.

        process = subprocess.Popen(
            [str(self.executable_path.absolute())],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        result = process.communicate(input_csv_text.encode())[0].decode()
        try:
            return pd.read_csv(StringIO(result))
        except:
            # Full text results (idtl = 5)
            outputs = result.split("Federal Tax Calculation:")[1:]
            column_names = [f"v{i}" for i in range(10, 30)]
            column_names = [i for i in column_names if i != "v23"]
            output_data = {column: [] for column in column_names}
            for output in tqdm(
                outputs, desc="Parsing detailed outputs from TAXSIM"
            ):
                columns_used = []
                for line in output.split("\n"):
                    if any(
                        [
                            name.replace("v", "") + "." in line
                            for name in column_names
                        ]
                    ):
                        number = line.split(".")[0].strip()
                        value = line.split(".")[1].split("  ")[-1]
                        name = f"v{number}"
                        if name in output_data and name not in columns_used:
                            output_data[name].append(int(value))
                            columns_used.append(name)
            return pd.DataFrame(output_data)

    def generate_from_microsimulation(
        self, dataset: Dataset, year: int, number: int
    ):
        sim = Microsimulation(dataset=dataset, year=2020)
        system: TaxBenefitSystem = sim.simulation.tax_benefit_system
        # system.add_variables_from_directory(self.folder / "variables")
        input_df = (
            sim.df(self.INPUT_VARIABLES, period=year)
            .sample(n=number * 100)
            .reset_index(drop=True)
        )
        input_df["idtl"] = 2  # Set full output
        for variable in self.UNIMPLEMENTED_VARIABLES:
            input_df[variable] = 0
        taxsim_df = self.calculate(input_df).reset_index(drop=True)
        taxsim_df = taxsim_df.T.apply(
            lambda row: [0] + list(row.values[:-1])
        ).T.drop(
            taxsim_df.columns[0], axis=1
        )  # Some issue with the TAXSIM dataframe now coming out in the right format
        taxsim_df = pd.concat(
            [
                input_df,
                taxsim_df,
            ],
            axis=1,
        )
        variables = system.variables
        i = 0
        test_str = ""
        tax_unit_number = 1
        # Shuffle the dataframe
        taxsim_df = (
            taxsim_df[taxsim_df[self.OUTPUT_VARIABLES].sum(axis=1) > 0]
            .sample(frac=1)
            .reset_index(drop=True)
        )
        for tax_unit_id in tqdm(taxsim_df.taxsimid, desc="Writing YAML tests"):
            if i >= number:
                break
            i += 1
            test_str += f"- name: Tax unit {tax_unit_number:,.0f} (CPS ID {tax_unit_id}) matches TAXSIM35 outputs\n  absolute_error_margin: 1\n  period: {year}\n  input:\n    people:\n"
            tax_unit_number += 1
            person_id = sim.calc("person_id").values
            person_tax_unit_id = sim.calc(
                "tax_unit_id", map_to="person"
            ).values
            tax_unit_ids = sim.calc("tax_unit_id").values
            people_in_tax_unit = person_id[person_tax_unit_id == tax_unit_id]
            person_number = 1
            for person in people_in_tax_unit:
                test_str += f"      person_{person_number}:\n"
                person_number += 1
                for variable_name in (
                    self.OPENFISCA_US_INPUT_VARIABLES + self.INPUT_VARIABLES
                ):
                    if variables[variable_name].entity.key == "person":
                        value = sim.calc(
                            variable_name, map_to="person"
                        ).values[person_id == person][0]
                        try:
                            test_str += (
                                f"        {variable_name}: {value:_.0f}\n"
                            )
                        except:
                            test_str += f"        {variable_name}: {value}\n"
            test_str += f"    tax_units:\n      tax_unit:\n        members: [{','.join(['person_' + str(p) for p in range(1, person_number)])}]\n"
            for variable_name in (
                self.OPENFISCA_US_INPUT_VARIABLES + self.INPUT_VARIABLES
            ):
                if variables[variable_name].entity.key == "tax_unit":
                    value = sim.calc(variable_name).values[
                        tax_unit_ids == tax_unit_id
                    ][0]
                    try:
                        test_str += f"        {variable_name}: {value:_.0f}\n"
                    except:
                        test_str += f"        {variable_name}: {value}\n"
            test_str += f"  output:\n"
            for variable_name in self.OUTPUT_VARIABLES:
                if variables[variable_name].entity.key == "tax_unit":
                    value = taxsim_df[variable_name][
                        taxsim_df.taxsimid == tax_unit_id
                    ].values[0]
                    try:
                        test_str += f"    {variable_name}: {value:_.0f}\n"
                    except:
                        test_str += f"    {variable_name}: {value}\n"
            test_str += "\n\n"
        return test_str


if __name__ == "__main__":
    taxsim = TaxSim35()
    result = taxsim.generate_from_microsimulation(CPS, 2022, number=32)
    print(result)
