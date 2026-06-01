from policyengine_us.model_api import *


class al_ccsp_copay_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP Section 3.3.1(vi) protective-service copay-waiver category"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=43"

    def formula(spm_unit, period, parameters):
        # State Plan Section 3.3.1(vi) waives the parental fee for children
        # authorized under the Protective Service, Foster Care, Early Head
        # Start, TANF-Other Relative, and Special Needs eligibility
        # categories. This flag models the Protective Service and Foster
        # Care members:
        #   - Foster Care (priority category #4): is_in_foster_care.
        #   - Protective Service (#5), i.e. children receiving or needing
        #     protective services in response to abuse / neglect /
        #     exploitation: receives_or_needs_protective_services.
        # The other three Section 3.3.1(vi) categories already waive the
        # copay through their own branches in al_ccsp_copay_waived:
        # Early Head Start (#6) via is_enrolled_in_head_start (the
        # Section 3.3.1(v) Head Start / EHS branch) and Special Needs (#8,
        # a qualifying diagnosis) via the Section 3.3.1(iv) disabled-child
        # branch.
        #
        # TANF-Other Relative (#7, child-only TANF) is NOT modeled: AL has
        # two TANF categories, JOBS (#1, work-mandatory) and TANF-Other
        # Relative (#7), and only #7 waives the copay. is_tanf_enrolled
        # cannot distinguish them, so keying off it would wrongly waive
        # JOBS families' copays.
        #
        # This flag is intentionally NARROWER than al_ccsp_protective_services
        # (the Section 2.2.2(f) *eligibility* definition), which also
        # includes homelessness. Homelessness is NOT a Section 3.3.1
        # copay-waiver category: the Section 3.3.1(iii) "families
        # experiencing homelessness" checkbox is left UNCHECKED, and AL
        # treats homelessness (priority category #2) as distinct from
        # Protective Services (#5) and Special Needs (#8) in its eight
        # eligibility categories (State Plan p. 31). A homeless-only family
        # is therefore eligible under Section 2.2.2(f) but still pays the
        # standard FPL-band fee.
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        has_protective_child = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        return has_foster_child | has_protective_child
