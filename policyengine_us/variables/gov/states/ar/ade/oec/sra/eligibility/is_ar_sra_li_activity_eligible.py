from policyengine_us.model_api import *


class is_ar_sra_li_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for Arkansas SRA Low-Income track"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=16"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= p.adult_age_threshold
        hours = person("weekly_hours_worked", period.this_year)
        # FSU §4.1.5.4: school converts to work-equivalent via 2.5 hr per
        # semester credit. Full-time college (12+ credits) implies 30+ hr
        # equivalent, satisfying LI's 30 hr/wk threshold. We don't extend
        # the proxy to K-12 students because the conversion rule applies to
        # post-secondary credit hours.
        is_student = person("is_full_time_college_student", period.this_year)
        meets_activity = (hours >= p.activity_hours_li) | is_student
        # All adults must meet the activity test.
        has_adult = spm_unit.sum(is_adult) > 0
        all_adults_qualify = spm_unit.sum(is_adult & ~meets_activity) == 0
        ccdf_fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (has_adult & all_adults_qualify) | ccdf_fallback
