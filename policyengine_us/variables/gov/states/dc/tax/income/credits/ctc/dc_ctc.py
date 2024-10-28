from policyengine_us.model_api import *
from numpy import ceil


class dc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ctc
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        income_threshold = p.income_threshold[filing_status]
        # For each $1000 above income threshold, the ctc amount decrease by $20.
        excess = max_(0, income - income_threshold)
        increments = ceil(excess / p.phase_out.increment)
        phase_out = increments * p.phase_out.amount

        capped_children = tax_unit("dc_ctc_capped_children", period)
        base_amount = p.amount * capped_children

        return max_(base_amount - phase_out, 0)
