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
        # family income" and "use the row above" to set the fee. The scan is
        # implemented literally — walking the rows bottom-up and keeping the
        # lowest row whose threshold exceeds income — because the chart's BB
        # row is below the AA row for family sizes 9 through 13, so a
        # count-of-thresholds-met shortcut would land those sizes one level
        # too high in the band between the BB and AA floors. Incomes below
        # the Level A floor stay at Level A; incomes no row exceeds (at or
        # above every floor) take the last level (BB).
        num_levels = len(SLIDING_FEE_LEVELS)
        first_greater = num_levels
        for index in reversed(range(num_levels)):
            threshold = thresholds[SLIDING_FEE_LEVELS[index]][capped_size]
            first_greater = where(threshold > income, index, first_greater)
        return max_(first_greater - 1, 0)
