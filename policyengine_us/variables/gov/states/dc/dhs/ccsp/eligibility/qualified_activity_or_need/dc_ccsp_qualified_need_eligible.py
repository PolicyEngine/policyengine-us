from policyengine_us.model_api import *


class dc_ccsp_qualified_need_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Child Care Subsidy Program (CCSP) due to qualified need"
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
        age_eligible = age < p.disabled_child
        has_disabled_child = spm_unit.any(is_dependent & is_disabled & age_eligible)
        # Income test waived when parent is disabled | child is homeless  | parent is teen parent (age <= 19)
        income_test_waived = spm_unit("dc_ccsp_income_test_waived", period)
        # Policy manual 2.4.2.6, children of elder caregivers: an individual
        # with responsibility for the day-to-day care of the child who is "age
        # 62 or older or receive[s] Social Security disability benefits or
        # Supplemental Security Income payments". The test is on the caregiver,
        # so both prongs are restricted to the head or spouse rather than
        # counting any household member's age or benefits.
        is_elderly = age >= p.elderly
        receives_ssdi_or_ssi = (
            add(person, period, ["social_security_disability", "ssi"]) > 0
        ) | person("receives_ssi", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_elder_caregiver = spm_unit.any(
            is_head_or_spouse & (is_elderly | receives_ssdi_or_ssi)
        )

        return has_disabled_child | income_test_waived | has_elder_caregiver
