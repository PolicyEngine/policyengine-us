from policyengine_us.model_api import *


class passive_estate_income(Variable):
    value_type = float
    entity = Person
    label = "Passive estate and trust income"
    unit = USD
    documentation = (
        "The section 469 passive subset of estate_income: Schedule E Part III "
        "line 34a column (d) passive income less line 34b column (c) passive "
        "deduction or loss allowed. It comes from Schedule K-1 (Form 1041) "
        "boxes 6 through 8 (business, rental real estate and other rental "
        "income) when they are passive to the beneficiary. Box 5 (royalties, "
        "annuities and income in respect of a decedent) is not subject to the "
        "passive activity rules and goes in the nonpassive columns (e) and "
        "(f), as does any other nonpassive amount, so it is not included here. "
        "Enter income as a positive amount and a loss as a negative amount. "
        "The default is zero: most estate and trust income is nonpassive (in "
        "tax year 2023, 38% of positive Schedule E Part III income was in "
        "column (d), SOI Publication 4801), so estate_income alone does not "
        "establish passive income. This classifies income already counted in "
        "estate_income and does not represent additional income."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.irs.gov/pub/irs-prior/f1040se--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-pdf/p4801.pdf#page=50",
        "https://www.law.cornell.edu/uscode/text/26/469",
    )
