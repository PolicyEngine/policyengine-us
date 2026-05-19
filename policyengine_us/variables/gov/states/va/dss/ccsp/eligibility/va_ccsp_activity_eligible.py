from policyengine_us.model_api import *


class va_ccsp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for Virginia Child Care Subsidy Program"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section20/",
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section30/",
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=36",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.activity
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_in_school = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        is_active = (hours_worked >= p.min_hours_per_week) | is_in_school
        meets_requirement = is_active | is_disabled
        has_active_parent = spm_unit.sum(is_head_or_spouse & is_active) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~meets_requirement) == 0
        modeled_eligible = has_active_parent & all_covered
        # meets_ccdf_activity_test covers activities not individually
        # modeled: job search, education/training, VIEW/SNAP E&T,
        # CPS referral, and temporary leave.
        ccdf_activity = spm_unit("meets_ccdf_activity_test", period.this_year)
        return modeled_eligible | ccdf_activity
