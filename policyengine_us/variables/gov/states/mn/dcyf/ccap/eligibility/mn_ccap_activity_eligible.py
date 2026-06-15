from policyengine_us.model_api import *


class mn_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota CCAP based on authorized activity"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.12, subd. 1(b) — minimum weekly hours for employed
        # caretakers (20) and working full-time students (10).
        "https://www.revisor.mn.gov/statutes/cite/142E.12",
        # Minn. Rules 3400.0040 — authorized activities (employment, job
        # search, education, training).
        "https://www.revisor.mn.gov/rules/3400.0040/",
    )

    def formula(spm_unit, period, parameters):
        # Each caretaker (sole parent or both parents in a two-parent
        # household) must be in an authorized activity. An employed caretaker
        # must work an average of at least 20 hours per week; a full-time
        # student must work at least 10 hours per week (Minn. Stat. 142E.12
        # subd. 1(b)). A disability can interrupt an authorized activity, so a
        # disabled caretaker is treated as meeting the requirement. We don't
        # track job-search status or the minimum-wage component at the moment,
        # so caretakers in job search and the minimum-wage test are not
        # separately captured here. We also don't track approved
        # education/training program enrollment at the moment, so the Minn.
        # Stat. 142E.12 subd. 3 education/training-only pathway (a non-employed
        # full-time student in an approved program, with no minimum
        # employment-hours requirement) is not modeled and such caretakers are
        # under-included here.
        p = parameters(period).gov.states.mn.dcyf.ccap.activity
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular
        # dependency in reform and microsimulation runs.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        meets_hours_floor = where(
            is_student,
            hours_worked >= p.student_min_weekly_hours,
            hours_worked >= p.min_weekly_hours,
        )
        in_authorized_activity = meets_hours_floor | is_disabled
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_inactive_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~in_authorized_activity) == 0
        )
        return has_caretaker & no_inactive_caretaker
