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
        fpg = spm_unit("spm_unit_fpg", period)
        # ARM 37.80.202(1): initial eligibility for income below 150% FPG (first-
        # time applicant). ARM 37.80.202(2): graduated eligibility for non-TANF
        # households at annual redetermination, income below 185% FPG. We proxy "at
        # redetermination / continuing recipient" with the mt_ccap_enrolled input;
        # first-time applicants (the default) use the 150% initial limit. The cap
        # is exclusive ("below"), so income exactly at the limit is not eligible.
        enrolled = spm_unit("mt_ccap_enrolled", period)
        fpg_rate = where(enrolled, p.fpg_limit.graduated, p.fpg_limit.initial)
        fpg_eligible = countable_income < fpg * fpg_rate
        # 85% SMI ineligibility overlay (45 CFR 98.20(a)(2) / Sliding Fee Scale).
        # With the 185% FPG ceiling the FPG limit binds first for all but the
        # largest households, so this rarely controls eligibility.
        smi = spm_unit("hhs_smi", period)
        smi_eligible = countable_income <= smi * p.income_limit_smi_rate
        income_eligible = fpg_eligible & smi_eligible
        # TANF cash-assistance families are categorically income eligible (TANF
        # child care pathway; their income is far below the FPG limits regardless).
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        return income_eligible | tanf_enrolled
