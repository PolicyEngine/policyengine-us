from policyengine_us.model_api import *


class amt_separate_addition(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income separate addition"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/55#d_2",
        # Line 4, married filing separately
        "https://www.irs.gov/pub/irs-prior/i6251--2025.pdf#page=9",
    )

    def formula(tax_unit, period, parameters):
        # 26 U.S.C. 55(d)(2) figures the increase on alternative minimum
        # taxable income "determined without regard to this sentence", so
        # with every other AMT adjustment, such as the refund and section 68
        # lines.
        amt_inc = tax_unit("amt_income_before_separate_addition", period)
        p = parameters(period).gov.irs.income.amt.exemption
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        reduced_amt_inc = max_(0, amt_inc - p.separate_limit)
        return (
            max_(
                0,
                min_(
                    p.amount[filing_status],
                    p.phase_out.rate * reduced_amt_inc,
                ),
            )
            * separate
        )
