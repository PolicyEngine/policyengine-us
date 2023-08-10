from policyengine_us.model_api import *
from numpy import ceil


class ct_income_tax_phase_out_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax phase out add back"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        p = parameters(period).gov.states.ct.tax.income.main.add_back
        filing_status = tax_unit("filing_status", period)
        start = p.start[filing_status]
        max_amount = p.max_amount[filing_status]
        increment = p.increment[filing_status]
        reduction_amount = p.amount[filing_status]
        excess = max_(income - start, 0)
        increments = ceil(excess / increment)
        amount = increments * reduction_amount
        return min_(max_amount, amount)
