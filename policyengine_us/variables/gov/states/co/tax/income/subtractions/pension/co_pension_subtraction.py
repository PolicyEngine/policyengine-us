from policyengine_us.model_api import *


class co_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado pension and annuity subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    # pension subtraction does not include social security subtraction
    adds = [
        "co_pension_subtraction_head",
        "co_pension_subtraction_spouse",
    ]
