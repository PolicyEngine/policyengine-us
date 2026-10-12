from policyengine_us.model_api import *


class ms_ccpp_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Mississippi CCPP countable earned income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=28"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.income
        # Rule 5.4: earned income of students under 18 is non-countable; the
        # countable wage list applies to adults only.
        age = person("age", period.this_year)
        is_excluded_student = person("is_in_k12_school", period.this_year) & (
            age < p.student_earner_age_limit
        )
        # Self-employment is counted as gross (Rule 5.3); a net business loss
        # does not offset other income, so floor the self-employment sum at zero.
        self_employment = max_(
            add(person, period, p.countable_income.self_employment_sources), 0
        )
        earned = person("employment_income", period) + self_employment
        return where(is_excluded_student, 0, earned)
