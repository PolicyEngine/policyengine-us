from policyengine_us.model_api import *


class mt_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Montana Best Beginnings Child Care Scholarship monthly copayment"
    definition_period = MONTH
    defined_for = "mt_ccap_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.copayment
        gmi = spm_unit("mt_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_ratio = where(fpg > 0, gmi / fpg, 0)

        # Non-TANF families pay the greater of GMI times the sliding-scale
        # percentage or the $10 minimum.
        sliding_copay = max_(gmi * p.copay_rate.calc(fpg_ratio), p.minimum)
        # TANF cash-assistance recipients pay a flat $10 minimum copayment.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        return where(tanf_enrolled, p.minimum, sliding_copay)
