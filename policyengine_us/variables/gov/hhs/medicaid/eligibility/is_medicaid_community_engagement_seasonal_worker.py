from policyengine_us.model_api import *


class is_medicaid_community_engagement_seasonal_worker(Variable):
    value_type = bool
    entity = Person
    label = "Seasonal worker for Medicaid community engagement"
    definition_period = YEAR
    default_value = False
    documentation = (
        "Whether the person is a seasonal worker for the Medicaid community "
        "engagement six-month average income pathway."
    )

