from policyengine_us.model_api import *


class amt_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    documentation = (
        "Alternative minimum taxable income, Form 6251 line 4: taxable income "
        "with the section 56 adjustments, plus the increase for a married "
        "individual filing a separate return."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/55#b_2",
        "https://www.law.cornell.edu/uscode/text/26/55#d_2",
        "https://www.irs.gov/pub/irs-prior/f6251--2025.pdf#page=1",
        # Line 4, married filing separately
        "https://www.irs.gov/pub/irs-prior/i6251--2025.pdf#page=9",
    )
    adds = ["amt_income_before_separate_addition", "amt_separate_addition"]
