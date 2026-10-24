from policyengine_us.model_api import *


class az_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Arizona LIHEAP countable unearned income"
    documentation = (
        "Gross unearned income of a household member: counted in full for "
        "members aged 18 and older, and for younger members only from policy "
        "revision 15 (March 23, 2026). Each source is floored at zero, so a "
        "rental loss does not offset other income, and Social Security is "
        "counted net of the Medicare Part B premium the person pays. Cash "
        "Assistance is a household benefit added in az_liheap_countable_income."
    )
    unit = USD
    reference = (
        # PDF pages 4, 8-9, 14
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=4",
        "https://web.archive.org/web/20251030203752/https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=9",
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.income
        # Gross Income is "The total Household income for all Household
        # members before taxes and other deductions" (page 4), and a loss is
        # not income, so each source is floored at zero and a rental loss
        # cannot offset another source. ADD sums the MONTH-defined ssi over
        # the year.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Section VII.A.1.c.ii.D note: "Expenses related to Medicare (such as
        # premiums) should be subtracted when determining gross income", and
        # plan Section 1.9 counts SSA benefits "Excluding MediCare deduction".
        # The premium is netted from the Social Security benefit it is
        # withheld from. medicare_part_b_premium is zero for a person who is
        # not enrolled and excludes the share a Medicare Savings Program pays;
        # no Part D premium input exists.
        premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period) - premium, 0)
        age = person("age", period)
        # Revision 13, Section VI.A.6.e.ii.E: "Income from Household members
        # under the age of 18 is not considered Countable Income." Revision 15
        # narrows this to "Earned income from Household members under the age
        # of 18", as revision 16A still reads. Counting a child's unearned
        # income from March 23, 2026 is an inference from that narrowing;
        # Section VI.A.6.d.ii still counts the income of members aged 18 and
        # older.
        counted = (age >= p.adult_age) | p.child_unearned_income_counted
        return where(counted, unearned + social_security, 0)
