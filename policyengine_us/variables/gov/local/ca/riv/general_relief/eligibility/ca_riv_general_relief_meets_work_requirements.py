from policyengine_us.model_api import *


class ca_riv_general_relief_meets_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets work requirements for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.local.ca.riv.general_relief.work_exempted_age
        # Person who is actively searching for jobs also qualify for work requirements
        is_working = (
            add(
                person, period, ["employment_income", "self_employment_income"]
            )
            > 0
        )
        # Elders are exempted from working
        # Full-time student in secondary school younger than certain age exempted from working
        age = person("monthly_age", period)
        is_full_time_student = person("is_full_time_student", period)
        in_secondary_school = person("is_in_secondary_school", period)
        qualify_person = is_full_time_student & in_secondary_school
        work_exempted_due_to_age = where(
            qualify_person, age < p.younger, age >= p.older
        )
        # Incapacitated or need to caring full time for a member of household
        has_incapable_of_self_care = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        return (
            is_working | work_exempted_due_to_age | has_incapable_of_self_care
        )
