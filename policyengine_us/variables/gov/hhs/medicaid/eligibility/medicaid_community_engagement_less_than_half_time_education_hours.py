from policyengine_us.model_api import *


class medicaid_community_engagement_less_than_half_time_education_hours(Variable):
    value_type = float
    entity = Person
    label = (
        "Medicaid community engagement monthly less-than-half-time education hours"
    )
    unit = "hour"
    definition_period = YEAR
    default_value = 0

