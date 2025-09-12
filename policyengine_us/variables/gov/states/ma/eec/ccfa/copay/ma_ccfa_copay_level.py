from policyengine_us.model_api import *


class ma_ccfa_copay_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Massachusetts CCSP copay level"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/parent-fee-chart-fy2025/download"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay.fee_level
        income = spm_unit("ma_ccfa_countable_income", period)
        family_size = spm_unit("spm_unit_size", period)
        capped_size = np.clip(family_size, 2, 12)
        fpg = spm_unit("ma_ccfa_fpg", period)

        # Calculate income as ratio of FPG
        income_ratio = income / fpg

        # Get the increment for this family size
        ratio_increment = p.income_ratio_increments[capped_size]

        # Calculate how many increments above 100% FPG the income is.
        levels_above_fpg = max_(0, income_ratio - 1) / ratio_increment

        fee_level = 1 + np.ceil(levels_above_fpg)

        return min_(fee_level, p.maximum_level)
