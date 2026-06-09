from policyengine_us.model_api import *


class in_ccdf_parent_in_eligible_activity(Variable):
    value_type = bool
    entity = Person
    label = "Indiana CCDF parent in an eligible activity"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=15"
    )

    def formula(person, period, parameters):
        # Qualifying activities include employment, self-employment, on-the-job
        # training, initial-application job search, education or training,
        # incapacitation, and CPS referral. There is no minimum number of
        # working hours. We treat any parent with earnings, any hours worked,
        # full-time student status, TANF enrollment, or a disability as being
        # in a qualifying activity; job search, education, training, and CPS
        # referral can additionally be set through this input.
        has_earnings = (
            add(person, period, ["employment_income", "self_employment_income"]) > 0
        )
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        is_tanf_enrolled = person.spm_unit("is_tanf_enrolled", period)
        return (
            has_earnings
            | (hours_worked > 0)
            | is_student
            | is_disabled
            | is_tanf_enrolled
        )
