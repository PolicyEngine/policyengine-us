from policyengine_us.model_api import *


class al_ccsp_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP copay waived"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=43"

    def formula(spm_unit, period, parameters):
        # Per Section 3.3.1, AL waives the parental fee for:
        #   (iv) families with a disabled child
        #   (v)  families with a Head Start / Early Head Start child
        #   (vi) children authorized under the Protective Service,
        #        Foster Care, EHS, TANF-Other Relative, and Special Needs
        #        categories (al_ccsp_copay_protective_services).
        # Section 3.3.1(iii) "families experiencing homelessness" is
        # UNCHECKED, so homeless-only families are NOT waived here even
        # though they qualify for eligibility under Section 2.2.2(f).
        #
        # The 7% federal copay cap (45 CFR 98.45(k)) is intentionally not
        # enforced: State Plan Section 3.1.1.a notes Alabama has submitted
        # a waiver and currently bills the flat per-child fee schedule.
        p_age = parameters(period).gov.states.al.dhr.ccsp.age
        person = spm_unit.members
        is_disabled = person("is_disabled", period.this_year)
        age = person("age", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_disabled_child = spm_unit.any(
            is_disabled & (age < p_age.disabled_child_limit) & is_dependent
        )
        has_head_start_child = add(spm_unit, period, ["is_enrolled_in_head_start"]) > 0
        protective_services = spm_unit("al_ccsp_copay_protective_services", period)
        return has_disabled_child | has_head_start_child | protective_services
