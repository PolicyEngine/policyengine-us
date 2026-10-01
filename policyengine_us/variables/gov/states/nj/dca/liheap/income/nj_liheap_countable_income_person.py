from policyengine_us.model_api import *


class nj_liheap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "New Jersey LIHEAP countable income per person"
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=6,7,8,9,10",
    )
    documentation = "Uses existing net self-employment inputs without extra deductions; flooring losses is a modeling convention. Child earnings follow the FY2026 plan. Social Security of children and documented veterans benefits are excluded by the handbook. SSI Lifeline supplements, gifts, foster payments, royalties and roomer receipts cannot be separately identified. The handbook uses a $500 monthly nonqualified-member disregard where older codified text says $268."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.income
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        adult = person("age", period) >= p.adult_age
        student_in_larger_household = person("is_full_time_student", period) & (
            person.spm_unit("spm_unit_size", period) > 1
        )
        earned = where(adult & ~student_in_larger_household, earned, 0)
        social_security = where(
            adult,
            max_(
                person("social_security", period)
                - person("medicare_part_b_premium", period),
                0,
            ),
            0,
        )
        income = earned + social_security + add(person, period, p.sources.unearned)
        qualified = person("is_citizen_or_legal_immigrant", period)
        # Read the handbook's singular-member rule as a per-person disregard.
        return where(
            qualified,
            income,
            max_(income - p.nonqualified_member_disregard * MONTHS_IN_YEAR, 0),
        )
