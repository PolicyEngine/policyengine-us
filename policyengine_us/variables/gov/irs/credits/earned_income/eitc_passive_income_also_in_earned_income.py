from policyengine_us.model_api import *


class eitc_passive_income_also_in_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Passive income or loss also included in EITC earned income"
    unit = USD
    documentation = (
        "The part of the person's passive partnership and S corporation income "
        "or loss (passive_partnership_s_corp_income) that is also included in "
        "earned income under 26 USC 32(c)(2). An example is a general "
        "partner's distributive share from a partnership in which they do not "
        "materially participate: it is passive under section 469 and net "
        "earnings from self-employment under section 1402(a). Enter income as "
        "a positive amount and a loss as a negative amount. 26 USC "
        "32(i)(2)(E) determines passive income and losses without regard to "
        "any amount included in earned income, so this amount is removed from "
        "the passive basket of the EITC investment income test. It classifies "
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
