from openfisca_us.model_api import *


class snap_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Standard Utility Allowance"
    unit = USD
    documentation = "The regular utility allowance deduction for SNAP"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        utility = parameters(period).usda.snap.income.deductions.utility
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        state = spm_unit.household("state_code_str", period)
        return 12 * select(
            [
                allowance_type == allowance_types.SUA,
                allowance_type == allowance_types.LUA,
                allowance_type == allowance_types.TUA,
                True,
            ],
            [utility.sua[state], utility.lua[state], utility.tua[state], 0],
        )
