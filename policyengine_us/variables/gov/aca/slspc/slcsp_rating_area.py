from policyengine_us.model_api import *


class slcsp_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        return where(
            household("in_la", period),
            household("slcsp_rating_area_la_county", period),
            household("slcsp_rating_area_default", period),
        )
