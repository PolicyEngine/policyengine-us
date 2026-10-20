from policyengine_us.model_api import *


class ma_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts LIHEAP due to income"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.liheap
        income = spm_unit("ma_liheap_income", period)
        income_threshold = spm_unit("ma_liheap_state_median_income_threshold", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 30 to 34 in 2022 to 2027. ma_liheap_fpg already uses the
        # guidelines in force on October 1 of the preceding year.
        floor = np.round(spm_unit("ma_liheap_fpg", period) * p.fpg_floor, 2)
        return (income <= income_threshold) | (income < floor)
