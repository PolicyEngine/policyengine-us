from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.limited_business_loss import (
    section_461l_business_income_and_loss,
)


class excess_business_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Excess business loss disallowed under section 461(l)"
    unit = USD
    documentation = (
        "The head and spouse's business losses beyond business income plus "
        "the section 461(l) threshold (Form 461 line 16): the part of their "
        "business losses that limited_business_loss does not deduct this "
        "year."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.irs.gov/pub/irs-prior/i461--2025.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        _, business_loss = section_461l_business_income_and_loss(tax_unit, period)
        return max_(0, business_loss - tax_unit("limited_business_loss", period))
