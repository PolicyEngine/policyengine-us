from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER

class EnhancedCPS(Dataset):
    name = "enhanced_cps"
    label = "Enhanced CPS"
    file_path = STORAGE_FOLDER / "enhanced_cps.h5"
    data_format = Dataset.ARRAYS
    time_period = "2023"

    def generate(self):
        raise NotImplementedError("Enhanced CPS is not yet implemented")
    
