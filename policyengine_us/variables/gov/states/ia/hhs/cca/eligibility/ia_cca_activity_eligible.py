from policyengine_us.model_api import *


class ia_cca_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Iowa CCA based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=6"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.activity_requirements
        # Each parent must average at least 32 hours per week in an approved
        # activity, or 28 hours when the family includes a child with
        # special needs (IAC 441-170.2(2)"b"(2)).
        has_special_needs_child = spm_unit("ia_cca_has_special_needs_child", period)
        min_hours = where(
            has_special_needs_child,
            p.weekly_hours_special_needs,
            p.weekly_hours,
        )
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular
        # dependency with the labor supply response.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        meets_work_requirement = hours_worked >= spm_unit.project(min_hours)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        # Each parent must independently meet an approved activity
        # (170.2(2)"b"). We simplify the "coinciding hours" rule for
        # two-parent families to a per-parent hours gate. Require at least
        # one head/spouse so a unit of only dependents does not pass.
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        all_parents_qualify = (n_parents >= 1) & (n_qualifying >= n_parents)
        # Fallback for approved activities we cannot derive directly
        # (PROMISE JOBS, time-limited job search or medical incapacity,
        # combined employment and training).
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_parents_qualify | fallback
