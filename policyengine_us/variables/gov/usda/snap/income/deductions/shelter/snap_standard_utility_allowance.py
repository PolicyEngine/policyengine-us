from policyengine_us.model_api import *


class snap_standard_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP Standard Utility Allowance"
    unit = USD
    documentation = "The standard utility allowance deduction for SNAP"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.income.deductions.utility.standard
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        region = spm_unit.household("snap_utility_region_str", period)
        size = spm_unit("snap_unit_size", period)
        MAX_SPM_SIZE = 10
        capped_size = min_(MAX_SPM_SIZE, size)
        sua_household_size_dependent = spm_unit(
            "snap_standard_utility_allowance_by_household_size", period
        )

        sua = where(sua_household_size_dependent, 0, p.main[region])

        # change the state code to NC for the states that do not depend on household size to prevent key error
        region = where(sua_household_size_dependent, region, "NC")

        sua = where(
            sua_household_size_dependent,
            p.by_household_size.amount[region][capped_size],
            sua,
        )

        # No proration needed - already using snap_unit_size which excludes ineligible members
        return where(allowance_type == allowance_types.SUA, sua, 0)
