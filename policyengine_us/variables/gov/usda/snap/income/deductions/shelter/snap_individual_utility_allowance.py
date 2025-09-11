from policyengine_us.model_api import *


class snap_individual_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP Individual Utility Allowance"
    unit = USD
    documentation = "The individual utility allowance deduction for SNAP"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        utility = parameters(period).gov.usda.snap.income.deductions.utility
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        region = spm_unit.household("snap_utility_region_str", period)
        expense_types = utility.single.utility_types
        sum_of_individual_allowances = sum(
            [
                utility.single[expense.replace("_expense", "")][region]
                for expense in expense_types
            ]
        )
        return where(
            allowance_type == allowance_types.IUA,
            sum_of_individual_allowances,
            0,
        )
