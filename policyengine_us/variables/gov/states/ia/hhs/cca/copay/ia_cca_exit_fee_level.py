from policyengine_us.model_api import *

# CCA Exit fee levels A through D, in ascending income order.
EXIT_FEE_LEVELS = ["A", "B", "C", "D"]


class ia_cca_exit_fee_level(Variable):
    value_type = int
    entity = Person
    label = "Iowa CCA Exit fee level index"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=12"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.copay.exit
        income = person.spm_unit("ia_cca_countable_income", period)
        size = person.spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, 1, 13).astype(int)
        # The fee chart selects the income-threshold table for each child
        # separately: the special-needs table for a child receiving
        # special-needs care (the disability flag is the proxy) and the
        # basic table otherwise, so the level is resolved per person.
        is_special_needs = person("is_disabled", period.this_year)
        # Per the CCA Exit fee chart's lookup rule (#page=2): move down the
        # family-size column to the "first row with an amount greater than
        # the monthly family income" and "use the row above" to set the fee.
        # Walking the rows bottom-up and keeping the lowest row whose
        # threshold exceeds income implements that scan literally; incomes
        # below the Level A floor stay at Level A, and incomes at or above
        # the last floor take the last level.
        num_levels = len(EXIT_FEE_LEVELS)
        first_greater = num_levels
        for index in reversed(range(num_levels)):
            level = EXIT_FEE_LEVELS[index]
            basic_threshold = p.income_thresholds_basic[level][capped_size]
            sn_threshold = p.income_thresholds_special_needs[level][capped_size]
            threshold = where(is_special_needs, sn_threshold, basic_threshold)
            first_greater = where(threshold > income, index, first_greater)
        return max_(first_greater - 1, 0)
