from policyengine_us.model_api import *


class al_ccsp_copay_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP Section 3.3.1(vi) protective-service copay-waiver category"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=43"

    def formula(spm_unit, period, parameters):
        # State Plan Section 3.3.1(vi) waives the parental fee only for
        # children authorized under the Protective Service, Foster Care,
        # Early Head Start, TANF-Other Relative, and Special Needs
        # eligibility categories.
        #
        # This is intentionally NARROWER than al_ccsp_protective_services
        # (the Section 2.2.2(f) *eligibility* definition), which also
        # includes homelessness. Homelessness is NOT a Section 3.3.1
        # copay-waiver category:
        #   - The Section 3.3.1(iii) "families experiencing homelessness"
        #     copay-waiver checkbox is left UNCHECKED in the State Plan.
        #   - Alabama treats homelessness (priority category #2) as
        #     distinct from Protective Services (#5) and Special Needs
        #     (#8) in its eight eligibility categories (State Plan p. 31).
        # A homeless-only family is therefore eligible under Section
        # 2.2.2(f) but still pays the standard FPL-band fee.
        #
        # Of the Section 3.3.1(vi) categories we model foster care here;
        # disabled children and Head Start / Early Head Start children
        # waive the copay through their own terms in al_ccsp_copay_waived.
        # Kinship care, child-welfare engagement, EHS-CCP, TANF-Other
        # Relative, and Special Needs are not separately tracked at the
        # moment.
        return add(spm_unit, period, ["is_in_foster_care"]) > 0
