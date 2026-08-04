from policyengine_us.model_api import *


class ne_child_care_subsidy_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy countable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dhhs.ne.gov/Documents/Title-392-Complete.pdf#page=13",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=3",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.income
        person = spm_unit.members
        # 392 NAC 3-005.03(17) excludes the earnings of in-school children.
        age = person("age", period)
        excluded_student = person("is_in_k12_school", period) & (
            age <= p.student_earner_age_threshold
        )
        earned = add(person, period, p.sources.earned)
        countable_earned = spm_unit.sum(earned * ~excluded_student)
        unearned = add(spm_unit, period, p.sources.unearned)
        return max_(countable_earned + unearned, 0)
