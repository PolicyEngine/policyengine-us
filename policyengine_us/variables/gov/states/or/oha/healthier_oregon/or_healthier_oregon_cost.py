from policyengine_us.model_api import *


class or_healthier_oregon_cost(Variable):
    value_type = float
    entity = Person
    label = "Oregon Healthier Oregon benefit cost"
    unit = USD
    definition_period = YEAR
    defined_for = "or_healthier_oregon_eligible"
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
    )

    # Cost is calculated using per capita Medicaid costs by eligibility group.
    adds = ["or_healthier_oregon_cost_if_enrolled"]
