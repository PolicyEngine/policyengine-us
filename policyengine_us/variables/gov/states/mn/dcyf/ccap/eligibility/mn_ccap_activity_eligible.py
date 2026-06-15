from policyengine_us.model_api import *


class mn_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota CCAP based on authorized activity"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Rules 3400.0040 — authorized activities (employment, job
        # search, education, training).
        "https://www.revisor.mn.gov/rules/3400.0040/",
    )

    def formula(spm_unit, period, parameters):
        # Each parent (sole parent or both parents in a two-parent household)
        # must be in an authorized activity: employment, job search, education,
        # or training. Minnesota imposes no minimum-hours bar at application, so
        # we treat an applicant caretaker as meeting the activity requirement
        # when employed, a student, or disabled (a disability can interrupt an
        # authorized activity). We don't track job-search status at the moment,
        # so caretakers in job search are not separately captured here.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular
        # dependency in reform and microsimulation runs.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_working = hours_worked > 0
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        in_authorized_activity = is_working | is_student | is_disabled
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_inactive_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~in_authorized_activity) == 0
        )
        return has_caretaker & no_inactive_caretaker
