from policyengine_us.model_api import *


class nj_liheap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "New Jersey LIHEAP countable income per person"
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 6, 7, 8, 9, 10.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=6",
        # PDF pages 6, 7, 8, 9, 11.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=6",
        # PDF pages 6, 7.
        "https://liheapch.acf.gov/docs/2026/state-plans/NJ_Plan_2026.pdf#page=6",
    )
    documentation = (
        "Uses existing net self-employment inputs without extra deductions. Each "
        "earned and unearned source is floored at zero, so a loss in one source "
        "does not offset another. Child earnings follow the FY2026 plan. Social "
        "Security counts net of the computed Medicare Part B premium; Social "
        "Security of children and documented veterans benefits are excluded by the "
        "handbook. The SSI variable carries no Tenants Lifeline supplement, so the "
        "handbook's SSI deduction has nothing to remove. Gifts, foster payments, "
        "royalties and roomer receipts cannot be separately identified. The "
        "handbook uses a $500 monthly nonqualified-member disregard while the "
        "readopted regulation still says $268."
    )

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
        # Handbook section 2.3.F.7(a) (page 10) deducts the Medicare Part B
        # premium from gross Social Security, and 2.3.E.8 (page 9) excludes the
        # Part B buy-in withheld from the check. The computed
        # medicare_part_b_premium is the out-of-pocket Part B premium, zero when
        # a Medicare Savings Program pays it.
        social_security = max_(
            person("social_security", period)
            - person("medicare_part_b_premium", period),
            0,
        )
        social_security = where(adult, social_security, 0)
        # Plan 1.8 (page 6) counts gross income and handbook 2.3.D (page 8)
        # counts receipts from rental property, so each unearned source is
        # floored like the earned sources: a loss in one source cannot offset
        # another.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period), 0)
        income = earned + social_security + unearned
        qualified = person("is_citizen_or_legal_immigrant", period)
        # Read the handbook's singular-member rule as a per-person disregard.
        return where(
            qualified,
            income,
            max_(income - p.nonqualified_member_disregard * MONTHS_IN_YEAR, 0),
        )
