from policyengine_us.model_api import *


class three_digit_zip_code(Variable):
    value_type = str
    entity = Household
    label = "Three-digit zipcode"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = np.array(household("zip_code", period)).astype(str)
        # Non-numeric values (e.g. the "UNKNOWN" default when a dataset
        # stores no zip codes) pass through unchanged; consumers treat any
        # non-matching value as a failed lookup.
        numeric = np.char.isdigit(zip_code)
        safe_zip = np.where(numeric, zip_code, "0")
        zip_code_3 = (safe_zip.astype(int) // 100).astype(str)
        return np.where(numeric, np.char.zfill(zip_code_3, 3), zip_code)
