from policyengine_us.model_api import *


class az_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Arizona LIHEAP countable unearned income"
    documentation = (
        "Gross unearned income of a household member: counted in full for "
        "members aged 18 and older, and for younger members only from policy "
        "revision 15 (March 23, 2026). Social Security is counted gross; the "
        "policy's Medicare premium subtraction is not applied. Cash Assistance "
        "is a household benefit added in az_liheap_countable_income."
    )
    unit = USD
    reference = (
        # Sections VI.A.6.d.ii and VI.A.6.e.ii.B-E (pages 8-9) and Section
        # VII.A.1.c.ii.C-F (pages 13-14).
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=8",
        # Section 1.9 (pages 6-7).
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.income
        # add() sums the MONTH-defined ssi over the year with the YEAR sources.
        unearned = add(person, period, p.sources.unearned)
        age = person("age", period)
        # Revision 13, Section VI.A.6.e.ii.E: "Income from Household members
        # under the age of 18 is not considered Countable Income." Revision 15
        # narrows this to "Earned income from Household members under the age
        # of 18", so a child's SSI, survivor benefits or child support count
        # from March 23, 2026.
        counted = (age >= p.adult_age) | p.child_unearned_income_counted
        return where(counted, unearned, 0)
