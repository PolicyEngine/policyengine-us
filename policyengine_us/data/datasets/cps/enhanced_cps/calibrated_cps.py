from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset
from policyengine_us.data.datasets.cps.cps import CPS_2023


class CalibratedCPS_2023(Dataset):
    name = "calibrated_cps_2023"
    label = "Calibrated CPS (2023)"
    file_path = STORAGE_FOLDER / "calibrated_cps.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"

    def generate(self):
        from .calibrate import calibrate

        new_data = {}
        cps = CPS_2023()
        cps_data = cps.load()
        adjusted_weights = calibrate(
            "cps_2023",
            time_period="2023",
            training_log_path="calibration_log_cps.csv.gz",
        )
        for variable in cps.variables:
            if variable == "household_weight":
                new_data[variable] = adjusted_weights
            elif "_weight" not in variable:
                new_data[variable] = cps_data[variable][...]

        self.save_dataset(new_data)
