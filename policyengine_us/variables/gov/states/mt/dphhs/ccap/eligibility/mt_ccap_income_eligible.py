from policyengine_us.model_api import *


class mt_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.income
        countable_income = spm_unit("mt_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        # ARM 37.80.202(1): initial eligibility for income below 150% FPG (first-
        # time applicant). ARM 37.80.202(2): graduated eligibility for non-TANF
        # households at annual redetermination, income below 185% FPG. We proxy "at
        # redetermination / continuing recipient" with the mt_ccap_enrolled input;
        # first-time applicants (the default) use the 150% initial limit.
        #
        # NOTE on the ARM (185%) vs operational Sliding Fee Scale (200% "EXIT")
        # ceiling: the published scale runs its graduated tier to 200% FPG, but
        # ARM 37.80.202(2)'s rule text caps graduated eligibility at 185% FPG. We
        # follow the ARM rule text (gov.states.mt.dphhs.ccap.income.fpg_limit.
        # graduated = 1.85). Raising it to 2.0 to match the operational scale is a
        # policy question pending DPHHS confirmation, so it is documented, not
        # changed. The copay scale retains its 190/195/200% brackets to mirror the
        # published table even though they are unreachable at the 185% ceiling.
        #
        # FPG uses an exclusive `<` ("below" in the ARM text); the 85% SMI overlay
        # below uses `<=` because 45 CFR 98.20(a)(2) frames it as remaining "at or
        # below" 85% SMI. The two comparators intentionally differ. (The exact-cent
        # FPG boundary is float32-precision sensitive since monthly income and
        # monthly FPG are each annual/12; unit tests pin the +/- $1 behavior.)
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
