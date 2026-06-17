from policyengine_us.model_api import *


class mt_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.income
        countable_income = spm_unit("mt_ccap_countable_income", period)
        # Operational sliding fee scale runs through 200% FPG (graduated tier);
        # the ARM body text 150% standard limit is superseded by the published
        # scale per the modeling decision.
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_eligible = countable_income <= fpg * p.fpg_limit
        # The sliding fee scale footnote sets an over-85%-SMI hard ineligibility
        # ceiling that overlays the FPG brackets.
        smi = spm_unit("hhs_smi", period)
        smi_eligible = countable_income <= smi * p.income_limit_smi_rate
        income_eligible = fpg_eligible & smi_eligible
        # TANF cash-assistance families are categorically income eligible.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        return income_eligible | tanf_enrolled
