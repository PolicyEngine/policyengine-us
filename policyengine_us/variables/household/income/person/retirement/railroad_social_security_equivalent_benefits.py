from policyengine_us.model_api import *


class railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement social security equivalent benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The part of a tier 1 Railroad Retirement Act annuity equal to the "
        "Social Security benefit the same work record would earn: the social "
        "security equivalent benefit (SSEB) on Form RRB-1099, box 5, net of "
        "repayments. IRC 86(d)(1)(B) counts it as a social security benefit, "
        "so section 86 taxes it together with title II benefits. The rest of "
        "the annuity, reported on Form RRB-1099-R, goes in "
        "taxable_railroad_pension_benefits and "
        "tax_exempt_railroad_pension_benefits."
    )
    uprating = "gov.ssa.uprating"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        "https://www.law.cornell.edu/uscode/text/26/86#d_4",
        # IRS Pub. 915 (2024): the SSEB portion of tier 1 is treated as a
        # social security benefit; Worksheet A line A adds box 5 of
        # Forms SSA-1099 and RRB-1099. PDF pages 2, 4.
        "https://www.irs.gov/pub/irs-prior/p915--2024.pdf#page=2",
    )
