from openfisca_us.model_api import *


class county_zip_code(Variable):
    value_type = str
    entity = Household
    label = "County code from zip code"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        is_unknown = zip_code == "UNKNOWN"
        zip_code = where(is_unknown, 0, zip_code).astype(int)
        return where(is_unknown, -1, ((zip_code % 1e5) // 1e2).astype(str))
