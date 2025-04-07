from policyengine_us.model_api import *


class ut_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    documentation = "Form TC-40, line 32"
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        income = tax_unit(
            "ut_income_tax_before_non_refundable_credits", period
        )
        credits = tax_unit("ut_non_refundable_credits", period)
        return max_(income - credits, 0)
