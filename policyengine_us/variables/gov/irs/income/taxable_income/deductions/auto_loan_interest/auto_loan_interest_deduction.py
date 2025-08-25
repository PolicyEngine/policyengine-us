from policyengine_us.model_api import *


class auto_loan_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Auto loan interest deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    )

    def formula(tax_unit, period, parameters):
        auto_loan_interest = add(tax_unit, period, ["auto_loan_interest"])
        p = parameters(period).gov.irs.deductions.auto_loan_interest
        capped_interest = min_(auto_loan_interest, p.cap)
        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the phaseout start amount based on filing status (line 4).
        phaseout_start = p.phase_out.start[filing_status]
        agi_pre_ald = tax_unit("adjusted_gross_income", period)
        # Get the excess amount, if any, in thousands of dollars (rounded up) [lines 5 and 6].
        excess = max_(agi_pre_ald - phaseout_start, 0)
        increments = np.ceil(excess / p.phase_out.increment)

        # Calculate the excess part phase out amount (line 7).
        phase_out_amount = increments * p.phase_out.step
        return max_(capped_interest - phase_out_amount, 0)
