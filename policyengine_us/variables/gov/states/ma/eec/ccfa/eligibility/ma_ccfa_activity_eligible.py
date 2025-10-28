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

        # Individual activity requirements
        hours_worked = person(
            "weekly_hours_worked_before_lsr", period.this_year
        )
        meets_work_requirement = hours_worked >= p.weekly_hours

        age = person("monthly_age", period)
        work_exempt_age = age >= p.work_exempt_age

        is_student = person("is_full_time_student", period)

        individually_eligible = (
            meets_work_requirement | work_exempt_age | is_student
        )

        # Family-level exemptions
        is_pregnant = person("is_pregnant", period)
        is_disabled = person("is_disabled", period)
        parent_exempt = is_head_or_spouse & (is_pregnant | is_disabled)
        family_exempt = spm_unit.any(parent_exempt)

        is_homeless = spm_unit.household("is_homeless", period)

        # All parents must meet requirements unless family is exempt
        all_parents_eligible = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )

        return all_parents_eligible | family_exempt | is_homeless
