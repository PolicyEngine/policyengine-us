from policyengine_us.model_api import *


class snap_proration_factor(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP proration factor"
    documentation = "Factor for prorating income and deductions based on eligible members only"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_1"

    def formula(spm_unit, period, parameters):
        # Per 273.11(c)(1): Deductible expenses are divided evenly among all members
        # including the ineligible ones. All but the ineligible alien's share is counted
        # as a deductible expense for the remaining household members.

        ineligible_alien_count = spm_unit(
            "snap_unit_ineligible_alien_count", period
        )
        total_size = spm_unit("spm_unit_size", period)
        # Avoid division by zero
        excluded_proration = where(
            total_size > 0, ineligible_alien_count / total_size, 0
        )

        return max_(1 - excluded_proration, 0)
