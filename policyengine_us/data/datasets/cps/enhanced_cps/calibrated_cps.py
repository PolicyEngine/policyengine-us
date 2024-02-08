from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset
from policyengine_us.data.datasets.cps.cps import CPS_2023


class CalibratedCPS_2023(Dataset):
    name = "calibrated_cps_2023"
    label = "Calibrated CPS (2023)"
    file_path = STORAGE_FOLDER / "calibrated_cps.h5"
    data_format = Dataset.TIME_PERIOD_ARRAYS
    time_period = 2023
    num_years: int = 3

    def generate(self):
        from .calibrate import calibrate

        new_data = {}
        cps = CPS_2023()
        cps_data = cps.load()
        for year in range(self.time_period, self.time_period + self.num_years):
            year = str(year)
            adjusted_weights = calibrate(
                "cps_2023",
                time_period=year,
                training_log_path="calibration_log_cps.csv.gz",
            )
            for variable in cps.variables:
                if variable not in new_data:
                    new_data[variable] = {}
                if variable == "household_weight":
                    new_data[variable][year] = adjusted_weights
                elif "_weight" not in variable and (
                    (year == str(self.time_period)) or ("_id" in variable)
                ):
                    new_data[variable][year] = cps_data[variable][...]

        self.save_dataset(new_data)
