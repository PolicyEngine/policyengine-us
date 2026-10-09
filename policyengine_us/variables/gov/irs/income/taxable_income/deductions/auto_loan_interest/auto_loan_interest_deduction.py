from policyengine_us.model_api import *


class auto_loan_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Auto loan interest deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.irs.gov/taxtopics/tc505",
        "https://www.irs.gov/pub/irs-pdf/p6126.pdf",
    )

    def formula(tax_unit, period, parameters):
        auto_loan_interest = add(
            tax_unit,
            period,
            ["qualified_passenger_vehicle_loan_interest"],
        )
        p = parameters(period).gov.irs.deductions.auto_loan_interest
        capped_interest = min_(auto_loan_interest, p.cap)
        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get the phaseout start amount based on filing status (line 4).
        phaseout_start = p.phase_out.start[filing_status]
        # 26 U.S.C. 163(h)(4)(C)(ii)(II): modified adjusted gross income adds
        # back income excluded under sections 911, 931 and 933 (Schedule 1-A,
        # line 3).
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        # Get the excess amount, if any, in thousands of dollars (rounded up) [lines 5 and 6].
        excess = max_(magi - phaseout_start, 0)
        increments = np.ceil(excess / p.phase_out.increment)

        # Calculate the excess part phase out amount (line 7).
        phase_out_amount = increments * p.phase_out.step
        return max_(capped_interest - phase_out_amount, 0)
