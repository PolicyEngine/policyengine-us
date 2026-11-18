from policyengine_us.model_api import *


class eitc_passive_income_also_in_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Passive partnership income or loss also included in EITC earned income"
    unit = USD
    documentation = (
        "The part of the person's passive_partnership_s_corp_income that is "
        "also included in earned income under 26 USC 32(c)(2): a partnership "
        "distributive share that is passive under section 469 and net earnings "
        "from self-employment under section 1402(a), as for a general partner "
        "who does not materially participate. The same amount must also be "
        "included in partnership_self_employment_net_earnings, which is what "
        "puts it in EITC earned income; nothing here checks that. An S "
        "corporation share is never net earnings from self-employment, so it "
        "has no such part. Enter income as a positive amount and a loss as a "
        "negative amount. It is a sum over the person's activities, so it can "
        "exceed the person's net passive income or net partnership "
        "self-employment earnings, or have the opposite sign, because each of "
        "those nets earned and unrelated passive amounts together; do not "
        "limit it to them. 26 USC 32(i)(2)(E) determines passive income and losses without "
        "regard to amounts included in earned income, so the head's and "
        "spouse's amounts are removed from the passive basket of the EITC "
        "investment income test; a dependent's are not read. It classifies "
        "part of passive_partnership_s_corp_income and is not additional "
        "income."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2_E",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/26/1402#a",
    )
