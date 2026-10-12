from policyengine_us.model_api import *


class amt_exemption(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax exemption"
    unit = USD
    documentation = (
        "AMT exemption amount after phase-out and kiddie tax adjustments. "
        "Form 6251, Line 5."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/55#d",  # 26 U.S.C. § 55(d)
        "https://www.law.cornell.edu/uscode/text/26/59#j",
        "https://www.law.cornell.edu/uscode/text/26/911#d_2",
        "https://www.irs.gov/instructions/i6251",
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

        # A reduced exemption amount is applied to kiddie tax filers
        kiddie_tax_applies = tax_unit("amt_kiddie_tax_applies", period)
        # IRC 59(j) uses earned income under IRC 911(d)(2), rather than
        # the EITC gross-income inclusion rule. Preserve the existing gross
        # earnings cap independently of EITC payroll exclusions.
        adj_earnings = tax_unit_non_dep_sum("adjusted_earnings", tax_unit, period)
        child_amount = p.exemption.child.amount

        exemption_cap = where(
            kiddie_tax_applies,
            adj_earnings + child_amount,
            np.inf,
        )

        return min_(reduced_exemption_amount, exemption_cap)
