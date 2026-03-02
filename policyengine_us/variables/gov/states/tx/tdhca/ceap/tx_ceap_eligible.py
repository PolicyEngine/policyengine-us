from policyengine_us.model_api import *


class tx_ceap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Texas Comprehensive Energy" " Assistance Program (CEAP)"
    )
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = "https://www.tdhca.texas.gov/sites/default/files/community-affairs/ceap/docs/24-LIHEAP-Plan.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.ceap
        p_hhs = parameters(period).gov.hhs.liheap

        income = add(spm_unit, period, ["irs_gross_income"])

        # Texas uses the higher of 150% FPG or 60% SMI
        # per the FY 2024 LIHEAP State Plan, Section 2.1
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = fpg * p.income_limit

        state_median_income = spm_unit("hhs_smi", period)
        smi_limit = state_median_income * p_hhs.smi_limit

        income_limit = max_(fpg_limit, smi_limit)

        return income <= income_limit
