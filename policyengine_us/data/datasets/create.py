from policyengine_us.data import (
    CPS_2019,
    CPS_2020,
    CPS_2021,
    CPS_2022,
    CalibratedPUFExtendedCPS_2022,
    EnhancedCPS_2022,
)
from policyengine_us.data.storage import STORAGE_FOLDER

datasets = [
    CPS_2019,
    CPS_2020,
    CPS_2021,
    CPS_2022,
    CalibratedPUFExtendedCPS_2022,
    EnhancedCPS_2022,
]

for dataset in datasets[5:]:
    print(f"Generating {dataset.name}...")
    dataset().generate()
