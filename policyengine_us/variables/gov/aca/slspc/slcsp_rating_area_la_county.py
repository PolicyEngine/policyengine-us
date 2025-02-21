from policyengine_us.model_api import *


class slcsp_rating_area_la_county(Variable):
    value_type = int
    entity = Household
    label = (
        "Second-lowest ACA silver-plan cost rating area in Los Angeles County"
    )
    definition_period = YEAR
    defined_for = "in_la"

    def formula(household, period, parameters):
        zip3 = household("three_digit_zip_code", period)
        p = parameters(period).gov.aca
        return p.la_county_rating_area[zip3]
