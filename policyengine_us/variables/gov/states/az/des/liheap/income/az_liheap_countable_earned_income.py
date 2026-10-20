from policyengine_us.model_api import *


class az_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Arizona LIHEAP countable earned income"
    documentation = (
        "Gross wages and reported net self-employment income of household "
        "members aged 18 and older. Each source is floored at zero, so a "
        "business loss does not offset other earnings. Earned income of members "
        "under 18 never counts."
    )
    unit = USD
    reference = (
        # PDF pages 8-9, 13
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=8",
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.income
        # Section VII.A.1.c.ii.B verifies "Profit or loss documentation from
        # self-employment" without saying whether a loss offsets other income,
        # so each net source is floored at zero (project convention).
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        # Section VI.A.6.d.ii counts "Income from all Household members aged 18
        # and older"; Section VI.A.6.e.ii.E excludes income of members under 18
        # in revision 13 and their earned income in revision 15, and the plan's
        # Section 1.9 leaves "Earned income of a child under the age of 18"
        # unchecked, so under-18 earnings never count.
        age = person("age", period)
        return where(age >= p.adult_age, earned, 0)
