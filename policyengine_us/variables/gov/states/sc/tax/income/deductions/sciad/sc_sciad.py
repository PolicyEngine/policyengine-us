from policyengine_us.model_api import *


class sc_sciad(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina Income Adjusted Deduction (SCIAD)"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm",)
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.deductions.sciad
        # SCIAD only exists starting 2026
        if not p.in_effect:
            return tax_unit("adjusted_gross_income", period) * 0
        filing_status = tax_unit("filing_status", period)
        # Get the base amount by filing status
        base_amount = p.amount[filing_status]
        # Get federal AGI for phase-out calculation
        agi = tax_unit("adjusted_gross_income", period)
        # Get phase-out parameters by filing status
        phase_out_start = p.phase_out.start[filing_status]
        phase_out_width = p.phase_out.width[filing_status]
        # Calculate phase-out fraction
        # fraction = (AGI - start) / width
        excess_agi = max_(0, agi - phase_out_start)
        phase_out_fraction = min_(1, excess_agi / phase_out_width)
        # Calculate reduction
        reduction = base_amount * phase_out_fraction
        # Round reduction down to nearest $10
        reduction_rounded = np.floor(reduction / 10) * 10
        return max_(0, base_amount - reduction_rounded)
