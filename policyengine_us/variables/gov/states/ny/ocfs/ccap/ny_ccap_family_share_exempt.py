from policyengine_us.model_api import *


class ny_ccap_family_share_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Exempt from the New York CCAP family share"
    defined_for = StateCode.NY
    documentation = (
        "New York exempts public assistance families, families experiencing "
        "homelessness, foster children, protective or preventive child care "
        "and child-only child care services units from the income-based "
        "family share under 18 NYCRR 415.3(e)(1). Public assistance includes "
        "Family Assistance, Safety Net Assistance and veteran assistance. "
        "PolicyEngine reads reported receipt of each program and the Family "
        "Assistance grant the family takes up, which ny_ccap_countable_income "
        "also counts. It does not read the Safety Net Assistance amount, "
        "which can include payments to unit members other than a parent or "
        "caretaker relative. "
        "OCFS ties the foster care, protective and preventive exceptions to "
        "the child that receives the assistance. PolicyEngine computes one "
        "family share per unit and waives all of it when any member "
        "qualifies, so the family also pays no share for a sibling in "
        "ordinary care. PolicyEngine separately computes a zero share for "
        "income at or "
        "below the state income standard under 415.3(e)(3)."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=19",
        "https://web.archive.org/web/20240522174244id_/https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=18",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=3",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.3",
        "https://www.nysenate.gov/legislation/laws/SOS/2",
    )

    def formula(spm_unit, period, parameters):
        # Read New York's own grant rather than the federal tanf aggregate,
        # which reaches child care expenses through other states' dependent
        # care deductions and would close a CCAP -> TANF -> CCAP cycle.
        public_assistance = (
            spm_unit("is_tanf_enrolled", period)
            | (spm_unit("ny_ccap_family_assistance", period) > 0)
            | spm_unit("ny_safety_net_assistance_received", period)
            | spm_unit("ny_veteran_assistance_received", period)
        )
        homeless = spm_unit.household("is_homeless", period.this_year)
        foster_care = add(spm_unit, period, ["is_in_foster_care"]) > 0
        protective_services = spm_unit(
            "ny_ccap_protective_services_case", period.this_year
        )
        preventive_services = (
            add(spm_unit, period, ["ny_ccap_receives_preventive_services"]) > 0
        )
        child_only_unit = spm_unit("ny_ccap_child_only_unit", period)
        return (
            public_assistance
            | homeless
            | foster_care
            | protective_services
            | preventive_services
            | child_only_unit
        )
