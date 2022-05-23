from openfisca_us.model_api import *


class county_zip_code(Variable):
    value_type = str
    entity = Household
    label = "County code from zip code"
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = household("zip_code", period).astype(int)
        return ((zip_code % 1e5) // 1e2).astype(str)
