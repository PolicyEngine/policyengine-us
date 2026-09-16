from policyengine_us.model_api import *


class ma_ccfa_copay_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Massachusetts CCFA copay level"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/parent-fee-chart-fy2025/download",
        "https://www.mass.gov/doc/parent-fee-chart-fy2026/download",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay.fee_level
        income = spm_unit("ma_ccfa_countable_income", period)
        family_size = spm_unit("spm_unit_size", period)
        capped_size = np.clip(family_size, 2, 12)
        # The chart anchors its brackets at the monthly FPG rounded to
        # the nearest dollar (printed as the fee level 1 ceiling);
        # np.floor(x + 0.5) rounds halves up like the chart, where
        # np.round would round them to the nearest even dollar.
        fpg = np.floor(spm_unit("ma_ccfa_fpg", period) + 0.5)

        # Fee level 1 covers income up to the FPG; each subsequent level
        # covers one more bracket width of monthly income.
        bracket_width = p.income_bracket_width[capped_size]
        income_above_fpg = max_(0, income - fpg)

        fee_level = 1 + np.ceil(income_above_fpg / bracket_width)

        return min_(fee_level, p.maximum_level)
