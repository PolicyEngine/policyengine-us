from policyengine_us.model_api import *


class unrecaptured_section_1250_gain_before_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unrecaptured section 1250 gain before losses"
    unit = USD
    documentation = (
        "Long-term capital gain, not otherwise ordinary income, that would be "
        "ordinary income if section 1250(b)(1) included all depreciation and "
        "the section 1250(a) percentage were 100 percent, before the losses "
        "the 28-percent rate gain does not absorb reduce it: line 13 of the "
        "Unrecaptured Section 1250 Gain Worksheet. "
        "schedule_d_unrecaptured_section_1250_gain subtracts those losses. "
        "Memo item: long_term_capital_gains already includes it. For an "
        "amount already reduced, as on Schedule D line 19, use "
        "unrecaptured_section_1250_gain; enter one or the other."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(6)(A)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_6_A_i",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Unrecaptured Section 1250 Gain Worksheet—Line 19, line 13",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=13",
        ),
    ]
