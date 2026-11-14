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
        "counts both Family Assistance and Safety Net Assistance as public "
        "assistance. PolicyEngine reads reported Family Assistance "
        "enrollment and the Family Assistance grant the family takes up, "
        "which ny_ccap_countable_income also counts. It does not read the "
        "Safety Net Assistance amount, which can include payments to unit "
        "members other than a parent or caretaker relative. The regulation "
        "covers a child receiving preventive as well as protective services, and "
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
        "https://web.archive.org/web/20240522174244id_/https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=18",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # Read New York's own grant rather than the federal tanf aggregate,
        # which reaches child care expenses through other states' dependent
        # care deductions and would close a CCAP -> TANF -> CCAP cycle.
        public_assistance = spm_unit("is_tanf_enrolled", period) | (
            spm_unit("ny_ccap_family_assistance", period) > 0
        )
        homeless = spm_unit.household("is_homeless", period.this_year)
        foster_care = add(spm_unit, period, ["is_in_foster_care"]) > 0
        protective_services = spm_unit(
            "ny_ccap_protective_services_case", period.this_year
        )
        return public_assistance | homeless | foster_care | protective_services
