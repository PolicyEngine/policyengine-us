from policyengine_us.model_api import *


class vt_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont capped non-refundable tax credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        credits = parameters(
            period
        ).gov.states.vt.tax.income.credits.non_refundable
        income_tax = tax_unit("vt_income_tax_before_credits", period)
        total_credit_value = add(tax_unit, period, credits)
        return min_(income_tax, total_credit_value)
