from policyengine_us.model_api import *

# Sliding-fee levels A through BB, in ascending income order.
SLIDING_FEE_LEVELS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "AA",
    "BB",
]


class ia_cca_sliding_fee_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Iowa CCA and CCA Plus sliding-fee level index"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=11"

    def formula(spm_unit, period, parameters):
        thresholds = parameters(
            period
        ).gov.states.ia.hhs.cca.copay.sliding_fee.income_thresholds
        income = spm_unit("ia_cca_countable_income", period)
        # The income thresholds run by family size 1 through 13 (13 means
        # 13 or more).
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, 1, 13).astype(int)
        # Per the fee chart's lookup rule (#page=1): move down the family-size
        # column to the "first row with an amount greater than the monthly
        # family income" and "use the row above" to set the fee. Each printed
        # threshold is therefore the inclusive floor of its own level, so the
        # level index is the highest level whose floor is at-or-below income:
        # (number of thresholds the income meets or exceeds) - 1.
        levels_met = 0
        for level in SLIDING_FEE_LEVELS:
            threshold = thresholds[level][capped_size]
            levels_met = levels_met + (income >= threshold)
        level_index = max_(levels_met - 1, 0)
        # Cap at the last level (index 27); incomes above the BB threshold
        # exceed the CCA Plus income limit and are screened out upstream.
        return min_(level_index, len(SLIDING_FEE_LEVELS) - 1)
