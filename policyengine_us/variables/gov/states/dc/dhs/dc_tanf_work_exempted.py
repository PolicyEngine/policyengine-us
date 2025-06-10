from policyengine_us.model_api import *


class dc_tanf_work_exempted(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Exempted from working requirement for DC Temporary Assistance for Needy Families (TANF)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19g"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.age_threshold
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("monthly_age", period)
        # only the old person can exempted
        too_old = spm_unit.any(head_or_spouse & (age > 60))
        # Single parent can exempted
        has_infant = spm_unit.any(age < 1)
        # only the pregnant person can exempted
        has_pregnant_person = add(spm_unit, period, ["is_pregnant"]) > 0
        has_incapable_person = (
            add(spm_unit, period, ["is_incapable_of_self_care"]) > 0
        )
        return (
            too_old | has_infant | has_pregnant_person | has_incapable_person
        )
