from policyengine_us.model_api import *


class head_start_housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Head Start housing costs"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ecfr.gov/current/title-45/section-1305.2"
    adds = "gov.hhs.head_start.housing_cost_adjustment.housing_cost_sources"
