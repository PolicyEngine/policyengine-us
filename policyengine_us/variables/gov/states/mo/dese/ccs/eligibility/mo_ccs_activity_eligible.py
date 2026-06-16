from policyengine_us.model_api import *


class mo_ccs_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Child Care Subsidy based on need for care"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://web.archive.org/web/20211208073247id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/050/05",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # The need for care is met by employment, training or education, or job
        # search. We don't track activity-hours verification at the moment, so
        # an applicant is treated as meeting the need when an activity is
        # present (Manual 2010.050.05-.20).
        is_working = person("weekly_hours_worked", period.this_year) > 0
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = is_working | is_student
        # Require at least one head/spouse, and require every head/spouse to
        # have a qualifying activity so an SPM unit of only dependents does not
        # vacuously pass.
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        return has_head_or_spouse & all_covered
