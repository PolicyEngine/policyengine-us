from policyengine_us.model_api import *


class mo_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.040",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-325",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-05/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # RSMo 208.040 grants Temporary Assistance only on behalf of a
        # dependent child; pregnancy alone does not qualify a household
        # (13 CSR 40-2.325 has no unborn-child provision).
        # The child need not be a payable unit member: an SSI child is
        # excluded from the unit but still establishes the case, and the
        # caretaker can be the sole cash-eligible unit member (DSS Manual
        # 0210.005.05: "when the only child in the EU receives SSI, explore
        # Temporary Assistance (TA) eligibility for the payee and/or second
        # parent").
        # Not modeled: deprivation of parental support (2.310(5)(A)),
        # citizenship and qualified-alien status (2.310(1)(B)-(C)),
        # conduct-based exclusions (drug felony, fugitive), and the
        # (9)(B) disregard-denial sanctions.
        has_dependent_child = add(spm_unit, period, ["mo_tanf_dependent_child"]) > 0
        # The unit must still contain someone to pay — a household whose
        # child and caretaker are both SSI recipients has no payable
        # members and receives no grant.
        unit_size = spm_unit("mo_tanf_assistance_unit_size", period)
        income_eligible = spm_unit("mo_tanf_income_eligible", period)
        resources_eligible = spm_unit("mo_tanf_resources_eligible", period)
        return (
            has_dependent_child & (unit_size > 0) & income_eligible & resources_eligible
        )
