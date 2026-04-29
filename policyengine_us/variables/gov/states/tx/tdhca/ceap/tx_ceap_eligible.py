from policyengine_us.model_api import *


class tx_ceap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas Comprehensive Energy Assistance Program (CEAP)"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/ceap/docs/24-LIHEAP-Plan.pdf#page=9",
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/docs/25-LIHEAP-Plan-DRAFT_0.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.ceap
        p_hhs = parameters(period).gov.hhs.liheap

        income = add(spm_unit, period, ["irs_gross_income"])

        # FPG-based limit (always applies)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = fpg * p.income_limit

        # SMI-based limit (FY 2024 only, removed in FY 2025+)
        # per FY 2024 State Plan Section 2.1 vs FY 2025 State Plan Section 2.1
        uses_smi = p.uses_smi_threshold
        state_median_income = spm_unit("hhs_smi", period)
        smi_limit = where(uses_smi, state_median_income * p_hhs.smi_limit, 0)

        income_limit = max_(fpg_limit, smi_limit)
        income_eligible = income <= income_limit

        # Categorical eligibility per 42 USC 8624(b)(2)(A)
        # and FY 2024 State Plan Section 1.4
        tanf = spm_unit("is_tanf_enrolled", period)
        snap = spm_unit("is_snap_eligible", period)
        person = spm_unit.members
        ssi = spm_unit.any(person("is_ssi_eligible", period))
        categorically_eligible = tanf | snap | ssi

        return income_eligible | categorically_eligible
