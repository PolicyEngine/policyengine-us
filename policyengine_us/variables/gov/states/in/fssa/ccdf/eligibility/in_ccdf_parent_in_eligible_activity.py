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
        # incapacitation, and CPS referral. Employment is documented by proof
        # of income with no minimum number of working hours, so a parent
        # qualifies with positive wages, nonzero self-employment income (a
        # business loss still evidences active self-employment), full-time
        # student status, TANF enrollment, or a disability. We don't capture
        # not-yet-paid new employment or active job search at the moment.
        has_earnings = (person("employment_income", period) > 0) | (
            person("self_employment_income", period) != 0
        )
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        is_tanf_enrolled = person.spm_unit("is_tanf_enrolled", period)
        return has_earnings | is_student | is_disabled | is_tanf_enrolled
