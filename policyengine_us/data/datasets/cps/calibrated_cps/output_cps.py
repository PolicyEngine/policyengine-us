from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
from typing import Type
import pandas as pd
from pathlib import Path


class OutputDataset(Dataset):
    data_format = Dataset.TABLES
    input_dataset: Type[Dataset]
    input_dataset_year: int
    output_year: int
    time_period: int

    @staticmethod
    def from_dataset(
        dataset: Type[Dataset],
        year: int = None,
        out_year: int = 2022,
    ):
        class OutputDatasetFromDataset(OutputDataset):
            name = f"{dataset.name}"
            label = f"{dataset.label}"
            input_dataset = dataset
            time_period = year or dataset.time_period
            output_year = out_year
            file_path = STORAGE_FOLDER / f"output_{dataset.name}.h5"

        return OutputDatasetFromDataset

    def generate(self):
        from policyengine_us import Microsimulation

        sim = Microsimulation(
            dataset=self.input_dataset(),
        )

        sim.default_calculation_period = self.output_year
        VARIABLES = [
            "income_tax",
            "employment_income",
            "adjusted_gross_income",
            "taxable_interest_income",
            "tax_exempt_interest_income",
            "non_qualified_dividend_income",
            "qualified_dividend_income",
            "self_employment_income",
            "capital_gains",
            "taxable_pension_income",
            "pension_income",
            "taxable_income",
            "snap",
            "social_security",
            "ssi",
            "household_count_people",
            "household_weight",
            "household_id",
            "age",
            "is_male",
        ]

        variables = sim.tax_benefit_system.variables

        household = pd.DataFrame()
        tax_unit = pd.DataFrame()
        person = pd.DataFrame()

        for variable in VARIABLES:
            variable_entity = variables[variable].entity.key
            if variable_entity != "household":
                household[variable] = sim.calculate(
                    variable, map_to="household"
                ).values
                household[f"{variable}_participants"] = sim.map_result(
                    sim.calculate(variable).values > 0,
                    variable_entity,
                    "household",
                )
                if variable_entity == "tax_unit":
                    tax_unit[variable] = sim.calculate(variable).values
                elif variable_entity == "person":
                    person[variable] = sim.calculate(variable).values
            else:
                household[variable] = sim.calculate(variable).values

            tax_unit["household_id"] = sim.calculate("tax_unit_household_id").values
            person["household_id"] = sim.calculate("household_id", map_to="person").values

        self.save_dataset(
            dict(
                household=household,
                tax_unit=tax_unit,
                person=person,
            )
        )
