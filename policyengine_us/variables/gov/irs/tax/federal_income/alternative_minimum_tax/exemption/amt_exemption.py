from policyengine_us.model_api import *


class amt_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax exemption"
    unit = USD
    documentation = (
        "AMT exemption amount after phase-out and, before 2018, the kiddie "
        "tax limitation. "
        "Form 6251, Line 5."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/55#d",  # 26 U.S.C. § 55(d)
        "https://www.law.cornell.edu/uscode/text/26/59#j",
        "https://www.law.cornell.edu/uscode/text/26/911#d_2",
        "https://www.law.cornell.edu/uscode/text/26/402#e_3",
        "https://www.irs.gov/pub/irs-prior/i6251--2017.pdf#page=11",
        "https://www.irs.gov/pub/irs-prior/i8615--2017.pdf#page=2",
        "https://www.irs.gov/instructions/i6251",
        "https://www.law.cornell.edu/uscode/text/26/55#d_4_A_iii",
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.income.amt
        phase_out = p.exemption.phase_out
        filing_status = tax_unit("filing_status", period)
        amt_income = tax_unit("amt_income", period)

        # Base exemption amount based on filing status
        base_exemption_amount = p.exemption.amount[filing_status]

        # Phase-out at higher income levels
        income_excess = max_(0, amt_income - phase_out.start[filing_status])
        exemption_phase_out = phase_out.rate * income_excess
        reduced_exemption_amount = max_(
            0,
            base_exemption_amount - exemption_phase_out,
        )

        # IRC 55(d)(4)(A)(iii) turns off the IRC 59(j) child limitation for
        # taxable years beginning after 2017, so every filer gets the
        # phased-out exemption.
        if not p.exemption.child.in_effect:
            return reduced_exemption_amount

        # A reduced exemption amount is applied to kiddie tax filers
        kiddie_tax_applies = tax_unit("amt_kiddie_tax_applies", period)
        # IRC 59(j) uses earned income under IRC 911(d)(2): "amounts
        # received as compensation for personal services". Traditional
        # elective deferrals are not treated as made available to the
        # employee (IRC 402(e)(3)). The 2017 Form 8615 instructions, for the
        # same children and the same 911(d)(2) definition, generally take
        # earned income from Form 1040 line 7 (taxable wages), so the cap
        # uses adjusted_earnings, which leaves out pre-tax payroll deductions.
        adj_earnings = tax_unit_non_dep_sum("adjusted_earnings", tax_unit, period)
        child_amount = p.exemption.child.amount

        exemption_cap = where(
            kiddie_tax_applies,
            adj_earnings + child_amount,
            np.inf,
        )

        return min_(reduced_exemption_amount, exemption_cap)
