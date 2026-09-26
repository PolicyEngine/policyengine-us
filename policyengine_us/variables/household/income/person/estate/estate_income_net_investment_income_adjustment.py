from policyengine_us.model_api import *


class estate_income_net_investment_income_adjustment(Variable):
    value_type = float
    entity = Person
    label = "Estate and trust income net investment income adjustment"
    unit = USD
    documentation = (
        "The beneficiary's section 1411 adjustment from Schedule K-1 (Form "
        "1041) box 14 code H, entered on Form 8960 line 7. It is negative when "
        "part of estate_income is not net investment income, such as income "
        "from a retirement account that a trust passes through (§ 1411(c)(5); "
        "Treas. Reg. § 1.1411-3(e)(5), Example 1). Form 8960 also adjusts "
        "modified AGI for some code H amounts; that MAGI adjustment is not "
        "modeled."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=7",
        "https://www.law.cornell.edu/cfr/text/26/1.1411-3#e_5",
    )
