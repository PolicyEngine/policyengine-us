from policyengine_us.model_api import *


class meets_snap_general_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for SNAP benefits via general work requirements"
    )
    definition_period = MONTH
    reference = "https://www.fns.usda.gov/snap/work-requirements"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements
        age = person("monthly_age", period)
        monthly_hours_worked = person("monthly_hours_worked", period)
        # Too old or too young can exempted from working
        worked_exempted_age = age < 16 | age > 59
        # At least works 30 hours a week
        is_working = monthly_hours_worked >= 30 * 4
        # Meeting work requirements for another program (TANF or unemployment compensation)
        receives_tanf_or_ui = (
            add(person, period, ["tanf", "unemployment_compensation"]) > 0
        )
        # Taking care of a child under six or an incapacitated person
        has_child = person.spm_unit.any(age < 6)
        has_incapacitated_person = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Studying in school or a training program at least half-time
        is_full_time_student = person("is_full_time_student", period)
        return (
            worked_exempted_age
            | is_working
            | receives_tanf_or_ui
            | has_child
            | has_incapacitated_person
            | is_disabled
            | is_full_time_student
        )
