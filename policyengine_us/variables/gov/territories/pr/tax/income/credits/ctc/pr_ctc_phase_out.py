from policyengine_us.model_api import *
from numpy import ceil


class pr_ctc_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Child Tax Credit phase-out"
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf#page=1"

    def formula(tax_unit, period, parameters):
        # line 2a: add PR income that was excluded
        income = add(
            tax_unit,
            period,
            ["adjusted_gross_income", "pr_gross_income_person"],
        )
        p = parameters(period).gov.irs.credits.ctc.phase_out
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        excess = max_(0, income - phase_out_threshold)
        increments = ceil(excess / p.increment)
        return increments * p.amount
