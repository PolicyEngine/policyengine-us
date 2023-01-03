from policyengine_us.model_api import *


class il_total_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL total tax"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.IL

    formula = sum_of_variables(
        ["il_income_tax_after_nonrefundable_credits", "il_use_tax"]
    )
