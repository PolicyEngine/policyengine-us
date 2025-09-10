from policyengine_us.model_api import *


class snap_deduction_proration_factor(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP deduction proration factor"
    documentation = "Factor for prorating deductions based on eligible members only"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_1"

    def formula(spm_unit, period, parameters):
        # Per 273.11(c)(1): Deductible expenses are divided evenly among all members
        # including the ineligible ones. All but the ineligible members' share is counted
        # as a deductible expense for the remaining household members.
        
        eligible_size = spm_unit("snap_unit_size", period.this_year)
        total_size = spm_unit("spm_unit_size", period.this_year)
        
        # Avoid division by zero
        return where(
            total_size > 0,
            eligible_size / total_size,
            0
        )