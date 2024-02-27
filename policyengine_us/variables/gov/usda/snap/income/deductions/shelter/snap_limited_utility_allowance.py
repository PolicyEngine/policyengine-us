from policyengine_us.model_api import *


class snap_limited_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP Limited Utility Allowance"
    unit = USD
    documentation = "The limited utility allowance deduction for SNAP"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        utility = parameters(period).gov.usda.snap.income.deductions.utility
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        region = spm_unit.household("snap_utility_region_str", period)
        return where(
            allowance_type == allowance_types.LUA,
            utility.limited.allowance[region],
            0,
        )
