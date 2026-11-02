from policyengine_us.model_api import *


class de_liheap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP countable income of a person before payroll deductions"
    defined_for = StateCode.DE
    reference = (
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5",
        # Historical manual sections 416, 418, 419 and 429.2.
        # PDF pages 33,35-38,41-42
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=33",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.income
        age = person("age", period)
        earned = add(person, period, p.sources.earned)
        # Manual 419.1 groups railroad retirement with Social Security benefits,
        # and plan 1.9 nets health deductions from them. Both sit in both
        # unearned lists, so Part B nets once against their sum.
        benefits = add(person, period, ["social_security", "railroad_benefits"])
        part_b = person("medicare_part_b_premium", period)
        benefit_adjustment = max_(benefits - max_(part_b, 0), 0) - benefits
        adult_income = earned + add(person, period, p.sources.unearned)
        # Manual 418 excludes minors' income except child support and Social
        # Security benefits, which 419.1 defines to include SSI and railroad
        # retirement.
        minor_income = add(person, period, p.sources.minor_unearned)
        income = (
            where(age >= p.earned_income_min_age, adult_income, minor_income)
            + benefit_adjustment
        )
        # The historical manual excludes ALL income of dependent full-time
        # college students under 22. The FY2026 plan is silent on this rule.
        student_exempt = (
            person("is_full_time_college_student", period)
            & person("is_tax_unit_dependent", period)
            & (age < p.student_income_exclusion_age)
        )
        # add() aggregates monthly SSI over the year. Net business income is
        # used without another expense deduction, and this person amount has no
        # floor: manual 418.3 verifies self-employment against Form 1040 adjusted
        # gross income, so a loss can offset other members' income. Pension-health
        # withholding cannot be inferred from generic ordinary or payroll premiums.
        return where(student_exempt, 0, income)
