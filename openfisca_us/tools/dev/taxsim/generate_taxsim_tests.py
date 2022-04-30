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
        "pwages",
        "swages",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        "otherprop",
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
    OUTPUT_VARIABLES = [
        "fiitax",
    ]
    OPENFISCA_US_INPUT_VARIABLES = [
        "mars",
        "employment_income",
        "age",
        "is_tax_unit_head",
        "is_tax_unit_spouse",
        "is_tax_unit_dependent",
        "employment_income",
        "self_employment_income",
        "dividend_income",
        "pension_income",
        "social_security",
        "unemployment_insurance",
        "tax_unit_childcare_expenses",
        "short_term_capital_gains",
        "long_term_capital_gains",
        "taxable_interest",
        "filer_partnerships_s_corp_income",
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
            self.executable_path.chmod(self.executable_path.stat().st_mode | stat.S_IEXEC)

    def calculate(self, input_data: dict) -> dict:
        if isinstance(input_data, pd.DataFrame):
            input_csv = input_data
        else:
            input_csv = pd.DataFrame({col: [value] if not isinstance(value, collections.Sequence) else value for col, value in input_data.items()})
        input_csv_text = input_csv.to_csv(index=False)
        # We would usually run: taxsim35.exe < input.csv > output.csv.
        # But we're in a Python interface, so we just want the output as a DataFrame.
        
        process = subprocess.Popen([str(self.executable_path.absolute())], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        result = process.communicate(input_csv_text.encode())[0].decode()
        return pd.read_csv(StringIO(result))

    def generate_from_microsimulation(self, dataset: Dataset, year: int):
        sim = Microsimulation(dataset=dataset, year=year)
        system: TaxBenefitSystem = sim.simulation.tax_benefit_system
        # system.add_variables_from_directory(self.folder / "variables")
        input_df = sim.df(self.INPUT_VARIABLES)
        taxsim_df = self.calculate(input_df)
        variables = system.variables
        i = 0
        test_str = ""
        tax_unit_number = 1
        for tax_unit_id in tqdm(taxsim_df.taxsimid, desc="Writing YAML tests"):
            if not (i % 1000) == 0:
                i += 1
                continue
            i += 1
            test_str += f"- name: Tax unit {tax_unit_number:,.0f} matches TAXSIM35 outputs\n  absolute_error_margin: 1\n  period: {year}\n  input:\n    people:\n"
            tax_unit_number += 1
            people_in_tax_unit = sim.calc("person_id")[sim.calc("tax_unit_id", map_to="person") == tax_unit_id].values
            person_number = 1
            for person in people_in_tax_unit:
                test_str += f"      person_{person_number}:\n"
                person_number += 1
                for variable_name in self.OPENFISCA_US_INPUT_VARIABLES:
                    if variables[variable_name].entity.key == "person":
                        value = sim.calc(variable_name)[sim.calc("person_id") == person].values[0]
                        test_str += f"        {variable_name}: {value:_.0f}\n"
            test_str += f"    tax_units:\n      tax_unit:\n        members: [{','.join(['person_' + str(p) for p in range(1, person_number)])}]\n"
            for variable_name in self.OPENFISCA_US_INPUT_VARIABLES:
                if variables[variable_name].entity.key == "tax_unit":
                    value = sim.calc(variable_name)[sim.calc("tax_unit_id") == tax_unit_id].values[0]
                    test_str += f"        {variable_name}: {value}\n"
            test_str += f"  output:\n"
            for variable_name in self.OUTPUT_VARIABLES:
                if variables[variable_name].entity.key == "tax_unit":
                    value = sim.calc(variable_name)[sim.calc("tax_unit_id") == tax_unit_id].values[0]
                    test_str += f"      {variable_name}: {value:_.0f}\n"
            test_str += "\n\n"
        return test_str
                    
    
if __name__ == "__main__":
    taxsim = TaxSim35()
    taxsim.calculate(dict(
        taxsimid=1,
        mstat=2,
        year=2022,
        ltcg=100_000,
    ))
    result = taxsim.generate_from_microsimulation(CPS, 2020)
    print(result)