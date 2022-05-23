from openfisca_us.model_api import *


class medicaid_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Medicaid rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        state = household("state_code_str", period)
        three_digit_zip_code = household("three_digit_zip_code", period)
        mra = parameters(period).hhs.medicaid.geography.medicaid_rating_area
        return mra[state][three_digit_zip_code]
