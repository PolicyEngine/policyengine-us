from policyengine_us.model_api import *


class ca_smc_general_assistance_meets_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets work requirements for San Mateo County General Assistance"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = "https://www.smcgov.org/media/153295/download?inline=#page=1"

    def formula(person, period, parameters):
        # We don't track caregiving for an ill parent/spouse/child/sibling,
        # the "child under 16" exemption (moot — minor children disqualify
        # the SPM unit), or HSA-approved training/rehabilitation programs at
        # the moment.
        p = parameters(period).gov.local.ca.smc.general_assistance.work_requirement
        weekly_hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_working_full_time = weekly_hours_worked >= p.weekly_hours_threshold
        is_senior = person("age", period.this_year) >= p.senior_exemption_age
        is_disabled = person("is_disabled", period)
        is_full_time_student = person("is_full_time_student", period)
        is_lep_household = person.household(
            "is_non_english_speaking_home", period.this_year
        )
        is_in_work_program = person("is_in_work_program", period)
        return (
            is_working_full_time
            | is_senior
            | is_disabled
            | is_full_time_student
            | is_lep_household
            | is_in_work_program
        )
