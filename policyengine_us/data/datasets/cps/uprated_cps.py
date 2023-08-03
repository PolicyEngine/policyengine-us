from policyengine_core.data import Dataset
from typing import Type
from pathlib import Path
from policyengine_us.data.storage import STORAGE_FOLDER


class UpratedCPS(Dataset):
    data_format = Dataset.ARRAYS

    @staticmethod
    def from_dataset(
        dataset: Type[Dataset],
        out_year: int = 2022,
        new_name: str = None,
        new_label: str = None,
        new_file_path: str = None,
        new_url: str = None,
    ):
        class UpratedCPSFromDataset(UpratedCPS):
            name = new_name or f"{dataset.name}_uprated_{out_year}"
            label = new_label or f"{dataset.label}"
            input_dataset = dataset
            time_period = out_year
            file_path = new_file_path or (
                STORAGE_FOLDER / f"{dataset.name}_uprated_{out_year}.h5"
            )
            url = new_url

        return UpratedCPSFromDataset

    def generate(self):
        from policyengine_us import Microsimulation

        input_dataset = self.input_dataset()
        simulation = Microsimulation(dataset=self.input_dataset)

        data = {}
        for variable in input_dataset.variables:
            try:
                data[variable] = simulation.calculate(
                    variable, period=self.output_year
                ).values
            except:
                data[variable] = input_dataset.load(variable)

        self.save_dataset(data)
