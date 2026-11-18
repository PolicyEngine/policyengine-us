from policyengine_us.model_api import *


class household_net_income_including_health_benefits(Variable):
    value_type = float
    entity = Household
    label = "Net income including health benefits"
    definition_period = YEAR
    unit = USD
    adds = ["household_net_income", "healthcare_benefit_value"]
    # household_net_income already counts the premium tax credit, as a
    # refundable tax credit, and healthcare_benefit_value counts it too.
    subtracts = ["premium_tax_credit_in_force"]
