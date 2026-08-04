from policyengine_us.model_api import *


class md_ccs_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maryland Child Care Scholarship (CCS) based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://earlychildhood.marylandpublicschools.org/system/files/filedepot/2/scholarship-brochure-4.pdf"

    def formula(spm_unit, period, parameters):
        # CCS Brochure (Eligibility Requirements): each parent in the household
        # must be working/employed, in an approved training program, or
        # attending school. We approximate per-parent with employment + student;
        # for activities we don't individually model (job training, job search,
        # SNAP E&T, temporary leave, etc.), users can override at the SPMUnit
        # level via the federal CCDF bare input meets_ccdf_activity_test.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_employed = hours_worked > 0
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = is_employed | is_student
        per_parent_check_passes = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return per_parent_check_passes | fallback
