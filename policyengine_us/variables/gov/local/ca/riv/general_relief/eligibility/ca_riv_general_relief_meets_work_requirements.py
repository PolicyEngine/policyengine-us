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
        # Check if person is a qualifying secondary school student
        age = person("monthly_age", period)
        is_full_time_student = person("is_full_time_student", period)
        in_secondary_school = person("is_in_secondary_school", period)
        is_qualifying_secondary_student = (
            is_full_time_student & in_secondary_school
        )
        # Age-based exemptions have different thresholds based on student status:
        # - Full-time secondary students: exempt if younger than threshold
        # - Non-students: exempt if older than threshold (senior citizens)
        work_exempted_due_to_age = where(
            is_qualifying_secondary_student,
            age < p.younger,  # Student exemption: too young
            age >= p.older,  # Senior exemption: too old
        )
        # Incapacitated or need to caring full time for a member of household
        has_incapable_of_self_care = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        return (
            is_working | work_exempted_due_to_age | has_incapable_of_self_care
        )
