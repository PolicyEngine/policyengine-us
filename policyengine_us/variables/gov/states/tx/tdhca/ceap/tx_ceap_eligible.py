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

        income = spm_unit("tx_ceap_countable_income", period)

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
        tanf = spm_unit("is_tanf_enrolled", period.first_month)
        snap = spm_unit("is_snap_eligible", period)
        # SSI categorical eligibility means receipt of SSI payments, so use
        # the computed benefit or the reported-receipt flag. is_ssi_eligible
        # omits the SSI income test and would qualify high-income households.
        person = spm_unit.members
        # A payment or reported receipt in any month of the year qualifies.
        # receives_ssi is a monthly flag: read each month explicitly rather
        # than requesting an annual aggregate, which would cache a summed value
        # under the annual key and change what other formulas read.
        first_month = period.first_month
        monthly_receipt = [
            person("receives_ssi", first_month.offset(month_offset))
            for month_offset in range(12)
        ]
        reported_any_month = np.any(monthly_receipt, axis=0)
        receives_ssi = (add(person, period, ["ssi"]) > 0) | reported_any_month
        ssi = spm_unit.any(receives_ssi)
        categorically_eligible = tanf | snap | ssi

        return income_eligible | categorically_eligible
