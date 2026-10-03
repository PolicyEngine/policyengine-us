from policyengine_us.model_api import *


class de_liheap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP countable income of a person before payroll deductions"
    defined_for = StateCode.DE
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5",
        # Historical manual sections 418 and 429.2, pages 35 and 41-42.
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=35,41,42",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.income
        age = person("age", period)
        earned = add(person, period, p.sources.earned)
        unearned = add(person, period, p.sources.unearned)
        income = where(age >= p.earned_income_min_age, earned, 0) + unearned
        # The historical manual excludes ALL income of dependent full-time
        # college students under 22. The FY2026 plan is silent on this rule.
        student_exempt = (
            person("is_full_time_college_student", period)
            & person("is_tax_unit_dependent", period)
            & (age < p.student_income_exclusion_age)
        )
        # add() aggregates monthly SSI over the year. Net business income is
        # used without another expense deduction. Medicare and pension health
        # deductions are deferred because their withheld amounts are unknown.
        return where(student_exempt, 0, income)
