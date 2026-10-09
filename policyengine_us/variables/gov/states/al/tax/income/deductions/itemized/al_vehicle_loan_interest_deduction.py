from policyengine_us.model_api import *


class al_vehicle_loan_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama qualified vehicle loan interest deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-15",
        # PDF pages 20, 31.
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=20",
        "https://www.revenue.alabama.gov/tax-policy/obbba/",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        # Section 40-18-15(a)(2) allows interest to the extent 26 U.S.C. 163
        # allows it, so Alabama takes the federal cap and phase-out from
        # 163(h)(4). The Department of Revenue phases the deduction out on
        # Alabama adjusted gross income (Form 40, line 10) rather than federal
        # modified adjusted gross income.
        interest = add(
            tax_unit,
            period,
            ["qualified_passenger_vehicle_loan_interest"],
        )
        p = parameters(period).gov.irs.deductions.auto_loan_interest
        # Worksheet lines 1 and 2.
        capped_interest = min_(interest, p.cap)
        # Worksheet lines 3 through 7.
        filing_status = tax_unit("filing_status", period)
        phase_out_start = p.phase_out.start[filing_status]
        al_agi = tax_unit("al_agi", period)
        excess = max_(al_agi - phase_out_start, 0)
        increments = np.ceil(excess / p.phase_out.increment)
        phase_out_amount = increments * p.phase_out.step
        # Worksheet line 8, for taxable years 2025 through 2028
        # (26 U.S.C. 163(h)(4)(A)).
        return p.in_effect * max_(capped_interest - phase_out_amount, 0)
