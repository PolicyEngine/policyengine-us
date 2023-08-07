from policyengine_us.model_api import *
from numpy import ceil


class ct_income_tax_higher_tax_recapture(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax higher tax recapture"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        p = parameters(period).gov.states.ct.tax.income.main.recapture.higher
        filing_status = tax_unit("filing_status", period)
        start = p.start[filing_status]
        max_amount = p.max_amount[filing_status]
        brackets = p.brackets[filing_status]
        amount = p.amount[filing_status]
        income_start = max_(income - start, 0)
        income_brackets = ceil(income_start / brackets)
        amount = income_brackets * amount
        return min_(max_amount, amount)
