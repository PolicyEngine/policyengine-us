# Updating microdata

If you are updating the microdata (e.g., modifying code in `cps.py`), you will need to regenerate the processed microdata file locally and add it as a new data release.

Steps:

1. Clear old microdata with `rm policyengine_us/data/storage/*.h5`
2. Generate new microdata in Python with a command like this: `python -c "from policyengine_us.data import CPS_2022; CPS_2022().generate()"`
3. Make a copy of the new microdata file with a name that includes the _bumped_ version number. For example, if PolicyEngine US is currently version 0.263.4 and you are updating the 2023 CPS in a minor-bump PR, run `cp policyengine_us/data/storage/cps_2022.h5 policyengine_us/data/storage/cps_2022_v0_263_5.h5`.
4. Upload this new file to [github.com/PolicyEngine/policyengine-us/releases](https://github.com/PolicyEngine/policyengine-us/releases), both overwriting the existing unversioned file (delete the old one) and adding the versioned file as a new release.
5. Update the `CPS_2022` class in `policyengine_us/data/cps.py` to point to the new versioned file, e.g. `new_url="release://policyengine/policyengine-us/cps-2023/cps_2022_v0_263_5.h5",`.
6. Verify that this works by downloading it, e.g. `python -c "from policyengine_us.data import CPS_2022; CPS_2022().download()"`.
