from policyengine_us.model_api import *


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax "
    unit = USD
    definition_period = YEAR
    documentation = "Form TC-40, line 39"
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ut_income_tax_before_refundable_credits", period)
        withheld_income_tax = tax_unit("ut_withheld_income_tax", period)
        credits = tax_unit("ut_refundable_credits", period)
        return max_(income - credits - withheld_income_tax, 0)
