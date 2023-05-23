from policyengine_us.model_api import *

# policyengine-core test ./policyengine_us/tests/policy/baseline/gov/states/mi/


class mi_earned_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.mi.tax.income.credits.eitc
        mi_eitc = eitc * p.match_rate
        return min_(mi_eitc, p.max_amount)
