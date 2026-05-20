from policyengine_us.model_api import *


class in_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana income tax before refundable credits"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/6"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        tax = add(tax_unit, period, ["in_agi_tax", "in_use_tax"])
        # Non-refundable 529 credit reduces tax to zero but not below
        credit_529 = tax_unit("in_529_plan_credit", period)
        return max_(tax - credit_529, 0)
