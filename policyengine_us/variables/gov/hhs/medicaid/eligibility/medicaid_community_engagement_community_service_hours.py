from policyengine_us.model_api import *


class medicaid_community_engagement_community_service_hours(Variable):
    value_type = float
    entity = Person
    label = "Medicaid community engagement monthly community service hours"
    unit = "hour"
    definition_period = YEAR
    default_value = 0
