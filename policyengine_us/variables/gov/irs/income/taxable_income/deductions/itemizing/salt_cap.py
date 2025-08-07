from policyengine_us.model_api import *


class salt_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT cap"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        max_cap = p.cap[filing_status]
        if p.phase_out.in_effect:
            agi = tax_unit("adjusted_gross_income", period)
            agi_excess = max_(0, agi - p.phase_out.threshold[filing_status])
            phase_out = p.phase_out.rate * agi_excess
            phased_out_cap = max_(0, max_cap - phase_out)
            if p.phase_out.floor.applies:
                floor = p.phase_out.floor.amount[filing_status]
                return max_(phased_out_cap, floor)
            return phased_out_cap
        return max_cap
