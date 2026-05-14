from policyengine_us.model_api import *


class ga_caps_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=33"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.activity_requirements
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.weekly_hours
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # Per Policy Manual §6.8.1.8, a disabled parent who cannot provide care
        # is exempt from the activity requirement; authorization is based on
        # the non-disabled parent's activity.
        individually_eligible = meets_work_requirement | is_student | is_disabled
        all_heads_meet = ~spm_unit.any(is_head_or_spouse & ~individually_eligible)
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_heads_meet | meets_ccdf
