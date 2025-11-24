from policyengine_us.model_api import *


class is_snap_ineligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Is an ineligible student for SNAP"
    documentation = "Whether this person is an ineligible student for SNAP and can not be counted towards the household size"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2015"

    def formula(person, period, parameters):
        student = person(
            "is_full_time_student", period
        )  # part-time students should also count
        age = person("age", period)
        p = parameters(period).gov.usda.snap.student
        age_eligible = p.age_threshold.calc(age)
        disabled = person("is_disabled", period)
        hours_worked = person("weekly_hours_worked_before_lsr", period)
        hours_eligible = hours_worked >= p.working_hours_threshold
        # The parental status applies to children under 6 (under 12
        # if no care available)
        # Single parents with children under 12 are also eligible
        is_parent = person("is_parent", period)
        return student & ~(
            age_eligible | disabled | hours_eligible | is_parent
        )
