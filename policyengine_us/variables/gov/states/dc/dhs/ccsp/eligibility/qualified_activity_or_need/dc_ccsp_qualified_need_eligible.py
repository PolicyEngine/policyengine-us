from policyengine_us.model_api import *


class dc_ccap_qualified_need_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Assistance Program (CCAP) due to qualified need"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.age_threshold
        person = spm_unit.members
        age = person("monthly_age", period)
        # child age < 19 and disabled
        is_dependent = person("is_tax_unit_dependent", period)
        is_disabled = person("is_disabled", period)
        child_under_19 = age < p.disabled_child
        has_disabled_child = spm_unit.any(
            is_dependent & is_disabled & child_under_19
        )
        # parent is disabled # income waived
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_disabled_parent = spm_unit.any(is_head_or_spouse & is_disabled)
        # child is homeless # income waived
        is_homeless = spm_unit("is_homeless")
        # parent is teen parent (age <= 19) # income waived
        is_teen_parent = age <= p.teen_parent
        has_teen_parent = spm_unit.any(is_head_or_spouse & is_teen_parent)
        # parent is age >= 62 or get social_security_disability or ssi
        is_elderly = age >= p.elderly
        received_ssd_or_ssi = (
            add(spm_unit, period, ["social_security_disability", "ssi"]) > 0
        )
        has_elderly_parent = (
            spm_unit.any(is_head_or_spouse & is_elderly) | received_ssd_or_ssi
        )

        return (
            has_disabled_child
            | has_disabled_parent
            | is_homeless
            | has_teen_parent
            | has_elderly_parent
        )
