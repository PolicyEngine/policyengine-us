from policyengine_us.model_api import *


class medicaid_community_engagement_six_month_average_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid community engagement preceding six-month average monthly income"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Average monthly Medicaid MAGI household income over the preceding six "
        "months for the seasonal-worker community engagement pathway."
    )
