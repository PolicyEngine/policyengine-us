from policyengine_us.model_api import *

# CCA Exit fee levels A through D, in ascending income order.
EXIT_FEE_LEVELS = ["A", "B", "C", "D"]


class ia_cca_exit_fee_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Iowa CCA Exit fee level index"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=12"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.copay.exit
        income = spm_unit("ia_cca_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, 1, 13).astype(int)
        # CCA Exit uses a separate income threshold table for basic care and
        # special-needs care.
        has_special_needs_child = spm_unit("ia_cca_has_special_needs_child", period)
        # Per the CCA Exit fee chart's lookup rule (#page=2): move down the
        # family-size column to the "first row with an amount greater than the
        # monthly family income" and "use the row above" to set the fee. Each
        # printed threshold is the inclusive floor of its own level, so the level
        # index is the highest level whose floor is at-or-below income:
        # (number of thresholds the income meets or exceeds) - 1.
        levels_met = 0
        for level in EXIT_FEE_LEVELS:
            basic_threshold = p.income_thresholds_basic[level][capped_size]
            sn_threshold = p.income_thresholds_special_needs[level][capped_size]
            threshold = where(has_special_needs_child, sn_threshold, basic_threshold)
            levels_met = levels_met + (income >= threshold)
        level_index = max_(levels_met - 1, 0)
        return min_(level_index, len(EXIT_FEE_LEVELS) - 1)
