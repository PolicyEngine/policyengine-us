from policyengine_us.model_api import *


class basic_income_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income phase-out"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        basic_income = add(tax_unit, period, ["basic_income_before_phase_out"])
        bi = parameters(period).gov.contrib.ubi_center.basic_income
        if bi.taxable:
            return 0
        p = bi.phase_out
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        threshold = p.threshold[filing_status]
        income_over_threshold = max_(0, agi - threshold)
        # Phase out as a rate above the threshold if selected.
        if p.by_rate:
            return min_(income_over_threshold * p.rate, basic_income)
        # Otherwise phase out linearly until the end of the region.
        phase_out_width = p.end[filing_status] - threshold
        pct_phase_out = min_(income_over_threshold / phase_out_width, 1)
        return basic_income * pct_phase_out
