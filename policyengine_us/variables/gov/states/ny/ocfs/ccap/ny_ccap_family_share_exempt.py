from policyengine_us.model_api import *


class ny_ccap_family_share_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Exempt from the New York CCAP family share"
    defined_for = StateCode.NY
    documentation = (
        "Categorical exceptions to the New York Child Care Assistance "
        "Program family share under 18 NYCRR 415.3(e)(1). Three of the "
        "exceptions are narrower here than in the regulation. New York "
        "counts both family assistance and safety net assistance as public "
        "assistance, but PolicyEngine has no safety net assistance variable, "
        "so only family assistance enrollment is read. The regulation covers "
        "a child receiving preventive as well as protective services, and "
        "PolicyEngine has no preventive services variable. The exception for "
        "a child care services unit comprised of the eligible children only "
        "is not modeled because PolicyEngine has no variable identifying a "
        "child-only assistance unit. The exception for a family with income "
        "at or below 100 percent of the state income standard is not read "
        "here: 415.3(e)(3) computes that family's share as zero, which "
        "ny_ccap_family_share applies arithmetically."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # is_tanf_enrolled reflects reported enrollment rather than the
        # computed tanf amount, so reading it does not close the
        # CCAP -> TANF -> child care expenses circular dependency.
        public_assistance = spm_unit("is_tanf_enrolled", period)
        homeless = spm_unit.household("is_homeless", period.this_year)
        foster_care = add(spm_unit, period, ["is_in_foster_care"]) > 0
        protective_services = spm_unit(
            "ny_ccap_protective_services_case", period.this_year
        )
        return public_assistance | homeless | foster_care | protective_services
