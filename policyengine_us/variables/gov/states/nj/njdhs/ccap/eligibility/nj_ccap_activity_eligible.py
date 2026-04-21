from policyengine_us.model_api import *


class nj_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Jersey CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=22",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.activity_requirements
        enrolled = spm_unit("nj_ccap_enrolled", period)
        min_hours = where(enrolled, p.weekly_hours_redetermination, p.weekly_hours)
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= spm_unit.project(min_hours)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        # Each parent must independently qualify (N.J.A.C. 10:15-5.2).
        # Require at least one head/spouse in the unit so an SPM unit
        # containing only dependents does not vacuously pass.
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        all_parents_qualify = (n_parents >= 1) & (n_qualifying >= n_parents)
        # Fallback for non-derivable activities (TANF recipients,
        # CP&P cases, job training combos).
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_parents_qualify | fallback
