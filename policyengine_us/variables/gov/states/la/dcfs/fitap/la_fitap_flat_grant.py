from policyengine_us.model_api import *


class la_fitap_flat_grant(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP flat grant"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap.flat_grant
        size = spm_unit("spm_unit_size", period.this_year)

        # For size > max_table_size: grant[max] + grant[excess] - adjustment
        is_over_max = size > p.max_table_size

        # Base amount (capped at max_table_size)
        capped_size = min_(size, p.max_table_size)
        base_amount = p.amount[capped_size]

        # Excess calculation for size > max_table_size
        excess_size = max_(size - p.max_table_size, 1)
        capped_excess_size = min_(excess_size, p.max_table_size)
        excess_amount = p.amount[capped_excess_size]

        return where(
            is_over_max,
            base_amount + excess_amount - p.excess_adjustment,
            base_amount,
        )
