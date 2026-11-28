from policyengine_us.model_api import *


class ut_homeowner_renter_relief_nontaxable_alimony(Variable):
    value_type = float
    entity = Person
    label = "Utah homeowner's/renter's relief alimony outside federal AGI"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Alimony received that federal gross income leaves out, which Utah "
        "counts as support money received in nontaxable income (Utah Code "
        "59-2a-101(20)(a)(iv)). Federal adjusted gross income already holds "
        "alimony under a divorce instrument executed before 2019, and "
        "nontaxable income covers only amounts excluded from adjusted gross "
        "income ((20)(a)), so only the rest is added and alimony counts once."
    )
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=4",
    )
    defined_for = StateCode.UT

    def formula(person, period, parameters):
        alimony = person("alimony_income", period)
        sources = parameters(period).gov.irs.gross_income.sources
        # Federal gross income holds taxable_alimony_income, the alimony under
        # pre-2019 divorce instruments, when that is a listed source.
        if "taxable_alimony_income" in sources:
            taxable_alimony = person("taxable_alimony_income", period)
            return max_(alimony - taxable_alimony, 0)
        return alimony
