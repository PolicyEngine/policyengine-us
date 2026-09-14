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
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        meets_work_requirement = hours_worked >= p.weekly_hours

        age = person("monthly_age", period)
        work_exempt_age = age >= p.work_exempt_age

        is_student = person("is_full_time_student", period)

        individually_eligible = meets_work_requirement | work_exempt_age | is_student

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

    def formula_2022_02_01(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.activity_requirements
        person = spm_unit.members
        parent = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        retired = person("is_retired", period.this_year)
        retirement_exempt = (
            person("monthly_age", period) >= p.work_exempt_age
        ) & retired
        student = person("is_full_time_student", period.this_year)
        disabled = person("is_disabled", period.this_year)
        individual = (hours >= p.weekly_hours) | retirement_exempt | student | disabled
        family_exempt = spm_unit.household("is_homeless", period.this_year)

        if p.expanded_service_needs:
            parental_leave = person("ma_ccfa_approved_parental_leave", period)
            # Only one parent can establish the parental-leave service need.
            one_parent_on_leave = spm_unit.sum(parent & parental_leave) <= 1
            leave_eligible = parental_leave & spm_unit.project(one_parent_on_leave)
            protective = person("ma_ccfa_approved_domestic_violence", period) | person(
                "ma_ccfa_approved_substance_use_treatment", period
            )
            pathway = person("ma_ccfa_approved_pathway", period)
            individual = individual | leave_eligible | protective | pathway
            deployed = person("ma_ccfa_approved_military_deployment", period)
            family_exempt = family_exempt | spm_unit.any(parent & deployed)

        all_parents_eligible = spm_unit.sum(parent & ~individual) == 0
        return all_parents_eligible | family_exempt
