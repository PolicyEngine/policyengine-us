from policyengine_us.model_api import *


class household_net_income_including_health_benefits(Variable):
    value_type = float
    entity = Household
    label = "Net income including health benefits"
    definition_period = YEAR
    unit = USD
    adds = ["household_net_income", "healthcare_benefit_value"]
