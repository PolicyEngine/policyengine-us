from policyengine_us.data.storage import STORAGE_FOLDER
from policyengine_core.data import Dataset


class EnhancedCPS_2023(Dataset):
    name = "enhanced_cps_2023"
    label = "Enhanced CPS (2023)"
    file_path = STORAGE_FOLDER / "enhanced_cps.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"
    url = "release://policyengine/policyengine-us/enhanced-cps-2023/enhanced_cps.h5"

    def generate(self):
        from .puf_extended_cps import PUFExtendedCPS_2023
        from .calibrate import calibrate

        new_data = {}
        cps = PUFExtendedCPS_2023()
        cps_data = cps.load()
        adjusted_weights = calibrate(
            "puf_extended_cps_2023",
            time_period="2023",
        )
        for variable in cps.variables:
            if variable == "household_weight":
                new_data[variable] = adjusted_weights
            elif "_weight" not in variable:
                new_data[variable] = cps_data[variable][...]

        self.save_dataset(new_data)
