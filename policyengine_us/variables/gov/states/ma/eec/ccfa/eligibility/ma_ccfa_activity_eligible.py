from policyengine_us.model_api import *


class ma_ccfa_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Child Care Financial Assistance (CCFA) due to activity"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://regulations.justia.com/states/massachusetts/606-cmr/title-606-cmr-10-00/section-10-04/"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.activity_requirements
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.weekly_hours

        age = person("monthly_age", period)
        work_exempt_age = age >= p.work_exempt_age

        is_student = person("is_full_time_student", period)
        is_disabled = person("is_disabled", period)

        activity_eligible = (
            meets_work_requirement | work_exempt_age | is_student | is_disabled
        )
        is_homeless = spm_unit.household("is_homeless", period)
        # All parents in household must meet requirements
        ineligible_parent = is_head_or_spouse & ~activity_eligible
        return (spm_unit.sum(ineligible_parent) == 0) | (is_homeless)
