from policyengine_us.model_api import *


class three_digit_zip_code(Variable):
    value_type = str
    entity = Household
    label = "Three-digit zipcode"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = np.array(household("zip_code", period)).astype(str)
        zip_code_3 = (zip_code.astype(int) // 100).astype(str)
        return np.char.zfill(zip_code_3, 3)
