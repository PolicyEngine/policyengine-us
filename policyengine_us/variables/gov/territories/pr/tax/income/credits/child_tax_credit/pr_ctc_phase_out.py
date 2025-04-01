from policyengine_us.model_api import *
from numpy import ceil


class pr_ctc_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico CTC reduction from income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # source: schedule 8812, line 2a - add in puerto rico income that was excluded
        income = tax_unit("adjusted_gross_income", period) + tax_unit("pr_gross_income", period)
        p = parameters(period).gov.irs.credits.ctc.phase_out
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        excess = max_(0, income - phase_out_threshold)
        increments = ceil(excess / p.increment)
        return increments * p.amount
