from policyengine_us.model_api import *


class estate_income_niit_magi_adjustment(Variable):
    value_type = float
    entity = Person
    label = "Estate and trust MAGI adjustment for the net investment income tax"
    unit = USD
    documentation = (
        "The change to Form 8960 modified adjusted gross income that comes with "
        "Schedule K-1 (Form 1041) box 14 code H amounts. Form 8960 requires a "
        "positive code H amount to increase MAGI by the same amount; a negative "
        "amount changes MAGI only when the trust indicates it. The default is "
        "the positive part of estate_income_net_investment_income_adjustment, "
        "which is exact for a single K-1. With several K-1s, or a trust-indicated "
        "negative MAGI adjustment, enter the total directly: netting code H "
        "amounts across K-1s before taking the positive part would lose MAGI "
        "increases (for example, +10,000 from one trust and -7,500 of excluded "
        "IRA income from another raise MAGI by 10,000, not 2,500)."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=11",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=4",
    )

    def formula(person, period, parameters):
        code_h = person("estate_income_net_investment_income_adjustment", period)
        return max_(0, code_h)
