from policyengine_us.model_api import *


class mt_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://archive.legmt.gov/bills/MCA/title_0520/chapter_0020/part_0070/section_0150/0520-0020-0070-0150.html",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.income
        countable_income = spm_unit("mt_ccap_countable_income", period)
        fpg = spm_unit("mt_ccap_fpg", period)
        # MCA 52-2-715(1) sets the threshold for applicants at no less than 185%
        # FPG, and the Sliding Fee Scale ends Standard Eligibility at that row.
        # ARM 37.80.202 still prints 150% and 185%; the statute and the scale
        # govern. The scale's Graduated Eligibility runs to 200% FPG for families
        # already on the program at annual redetermination. We proxy "at
        # redetermination / continuing recipient" with the mt_ccap_enrolled input.
        #
        # The scale prints the top income of each row to the nearest dollar, and a
        # family at that income belongs to the row, so the test is at or below the
        # rounded limit. Round to cents first so floating-point noise can't move a tie.
        enrolled = spm_unit("mt_ccap_enrolled", period)
        fpg_rate = where(enrolled, p.fpg_limit.graduated, p.fpg_limit.initial)
        fpg_limit = np.floor(np.round(fpg * fpg_rate, 2) + 0.5)
        fpg_eligible = countable_income <= fpg_limit
        # 85% SMI ineligibility overlay (45 CFR 98.20(a)(2) / Sliding Fee Scale).
        # The FPG limit binds first for all but the largest households, so this
        # rarely controls eligibility.
        smi = spm_unit("hhs_smi", period)
        smi_eligible = countable_income <= smi * p.income_limit_smi_rate
        income_eligible = fpg_eligible & smi_eligible
        # TANF cash-assistance families are categorically income eligible (TANF
        # child care pathway; their income is far below the FPG limits regardless).
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        return income_eligible | tanf_enrolled
