from policyengine_us.model_api import *


class ms_ccpp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Mississippi CCPP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=30"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular dependency
        # with the labor supply response cycle.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        meets_work_requirement = hours_worked >= p.activity_hours
        # Full-time school or approved training also satisfies the requirement.
        is_student = person("is_full_time_student", period.this_year)
        # The activity requirement is waived for an SSI-disabled parent.
        is_ssi_disabled = person("is_ssi_disabled", period.this_year)
        individually_eligible = meets_work_requirement | is_student | is_ssi_disabled
        # Require at least one head/spouse so a unit of only dependents does not
        # vacuously pass, and require every head/spouse to be individually
        # eligible.
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        return has_head_or_spouse & all_covered
