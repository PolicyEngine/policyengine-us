from policyengine_us.model_api import *


class ut_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Earned Income Tax Credit"
    unit = USD
    documentation = "This credit is a fraction of the federal EITC."
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula_2022(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.earned_income
        eitc = tax_unit("eitc", period)
        limiting_liability = tax_unit(
            "ut_income_tax_before_credits", period
        ) - tax_unit("ut_taxpayer_credit", period)
        value = p.rate * eitc
        if not p.refundable:
            return min_(value, limiting_liability)
        return value
