from policyengine_us.model_api import *


class co_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado pension and annuity subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = [
        "co_pension_subtraction_indv",
        "co_social_security_subtraction_indv",
    ]
