from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset
from .puf_extended_cps import PUFExtendedCPS_2022


class CalibratedDataset(Dataset):
    data_format = Dataset.TIME_PERIOD_ARRAYS
    time_period = None
    num_years: int = None
    input_dataset = None

    def generate(self):
        from .calibrate import calibrate

        new_data = {}
        cps = self.input_dataset(require=True)
        cps_data = cps.load()
        for year in range(self.time_period, self.time_period + self.num_years):
            year = str(year)
            adjusted_weights = calibrate(
                cps,
                time_period=year,
                training_log_path=STORAGE_FOLDER / "calibration_log.csv.gz",
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


class CalibratedPUFExtendedCPS_2022(CalibratedDataset):
    name = "calibrated_puf_extended_cps_2022"
    label = "Calibrated PUF-extended CPS (2022-34)"
    input_dataset = PUFExtendedCPS_2022
    time_period = 2022
    num_years = 4
    file_path = STORAGE_FOLDER / "calibrated_puf_extended_cps_2022.h5"
