from policyengine_us.model_api import *


class ny_ccap_family_share_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Exempt from the New York CCAP family share"
    defined_for = StateCode.NY
    documentation = (
        "Categorical exceptions to the New York Child Care Assistance "
        "Program family share under 18 NYCRR 415.3(e)(1). The income "
        "exception — a family with income at or below 100 percent of the "
        "state income standard — is applied in ny_ccap_family_share itself "
        "rather than here. The sixth exception, a child care services unit "
        "comprised of the eligible children only, is not modeled because "
        "PolicyEngine has no variable identifying a child-only assistance "
        "unit."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://ocfs.ny.gov/main/policies/external/ocfs_2021/ADM/21-OCFS-ADM-14.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # is_tanf_enrolled reflects reported enrollment rather than the
        # computed tanf amount, so reading it does not close the
        # CCAP -> TANF -> child care expenses circular dependency.
        public_assistance = spm_unit("is_tanf_enrolled", period)
        homeless = spm_unit.household("is_homeless", period.this_year)
        foster_care = spm_unit.any(person("is_in_foster_care", period))
        protective_services = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        return public_assistance | homeless | foster_care | protective_services
