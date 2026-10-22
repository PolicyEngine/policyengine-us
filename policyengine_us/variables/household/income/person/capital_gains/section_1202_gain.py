from policyengine_us.model_api import *


class section_1202_gain(Variable):
    value_type = float
    entity = Person
    label = "Section 1202 gain before netting"
    unit = USD
    documentation = (
        "The gain on qualified small business stock that section 1202 would "
        "exclude but for its percentage limit, less the gain it excludes, "
        "before the losses the 28% Rate Gain Worksheet nets against it: line "
        "2 of that worksheet. capital_gains_28_percent_rate_gain nets it with "
        "collectibles gain or loss and the losses of 26 U.S.C. 1(h)(4)(B). "
        "Memo item: long_term_capital_gains already includes it. For an "
        "amount already netted, as on Schedule D line 18, use "
        "long_term_capital_gains_on_small_business_stock; enter one or the "
        "other."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(7)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_7",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), 28% Rate Gain Worksheet—Line 18, line 2",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=11",
        ),
    ]
