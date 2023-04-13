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

        PERSON_VARIABLES = [
            "age",
            "person_household_id",
        ]

        HOUSEHOLD_VARIABLES = [
            "household_id",
            "household_weight",
        ]

        PROGRAM_VARIABLES = [
            "income_tax",
        ]

        variables = sim.tax_benefit_system.variables

        person = pd.DataFrame()

        for variable in PERSON_VARIABLES:
            person[variable] = sim.calculate(variable, map_to="person").values

        household = pd.DataFrame()

        for variable in HOUSEHOLD_VARIABLES:
            household[variable] = sim.calculate(variable).values

        for variable in PROGRAM_VARIABLES:
            if variables[variable].entity.key != "household":
                person[variable] = sim.calculate(
                    variable, map_to="person"
                ).values
                household[variable] = sim.calculate(
                    variable, map_to="household"
                ).values
                household[f"{variable}_participants"] = sim.map_result(
                    sim.calculate(variable).values > 0,
                    variables[variable].entity.key,
                    "household",
                )
            else:
                household[variable] = sim.calculate(variable).values

        person["person_household_id"] = sim.calculate(
            "household_id", map_to="person"
        ).values

        self.save_dataset(
            dict(
                person=person,
                household=household,
            )
        )
