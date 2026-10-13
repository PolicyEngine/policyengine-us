from policyengine_us.model_api import *


class passive_estate_income(Variable):
    value_type = float
    entity = Person
    label = "Passive estate and trust income"
    unit = USD
    documentation = (
        "The section 469 passive part of estate_income: Schedule E Part III "
        "line 34a column (d) passive income less line 34b column (c) passive "
        "deduction or loss allowed. It comes from Schedule K-1 (Form 1041) "
        "boxes 6 through 8 (business, rental real estate and other rental "
        "income) when they are passive to the beneficiary. Box 5 (royalties, "
        "annuities and income in respect of a decedent) is not subject to the "
        "passive activity rules and goes in the nonpassive columns (e) and "
        "(f), with any other nonpassive amount. Enter income as a positive "
        "amount and a loss as a negative amount. The default treats all of "
        "estate_income as passive, as the model treats its undifferentiated "
        "rental income; enter the passive amount directly when part of "
        "estate_income is nonpassive. It classifies part of estate_income and "
        "is not additional income."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/f1040se--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/469",
    )

    def formula(person, period, parameters):
        return person("estate_income", period)
