from policyengine_us.model_api import *


class three_digit_zip_code(Variable):
    value_type = str
    entity = Household
    label = "Three-digit zipcode"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = pd.Series(np.asarray(household("zip_code", period)).astype(str))
        digits = zip_code.str.strip().str.extract(r"^(\d{1,5})", expand=False)
        result = pd.Series("", index=zip_code.index, dtype=object)
        has_digits = digits.notna()
        result[has_digits] = digits[has_digits].str.zfill(5).str[:3]
        return result.to_numpy(dtype=str)
