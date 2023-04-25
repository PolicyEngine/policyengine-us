from policyengine_us.model_api import *


class ut_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxpayer credit"
    unit = USD
    documentation = "Form TC-40, line 20"
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        initial_credit = tax_unit("ut_taxpayer_credit_max", period)
        reduction = tax_unit("ut_taxpayer_credit_reduction", period)
        max_value = max_(initial_credit - reduction, 0)
        limiting_liability = tax_unit("ut_income_tax_before_credits", period)
        if not parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.refundable:
            return min_(max_value, limiting_liability)
        return max_value
