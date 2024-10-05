from policyengine_us.model_api import *


class exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemptions"
    definition_period = YEAR
    documentation = "Personal exemptions amount after phase-out"
    unit = USD

    def formula(tax_unit, period, parameters):
        # calculate exemptions amount before phase-out
        exemptions = tax_unit("exemptions_count", period)
        p = parameters(period).gov.irs.income.exemption
        amount = exemptions * p.amount
        # calculate exemptions amount after phase-out
        filing_status = tax_unit("filing_status", period)
        phase_out_start_agi = p.phase_out.start[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        excess_agi = max_(0, agi - phase_out_start_agi)
        phase_out_step_size = p.phase_out.step_size[filing_status]
        steps = excess_agi / phase_out_step_size
        phase_out_fraction = steps * p.phase_out.rate
        return max_(0, amount * (1 - phase_out_fraction))
