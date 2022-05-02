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
        region = spm_unit("snap_utility_region", period)
        sua_due = where(allowance_type == allowance_types.SUA, utility.standard[region], 0)
        lua_due = where(allowance_type == allowance_types.LUA, utility.limited[region], 0)
        expense_types = utility.utility_types
        sum_of_individual_allowances = sum([utility[expense.replace("_expense", "")][region] for expense in expense_types])
        iua_due = where(allowance_type == allowance_types.IUA, sum_of_individual_allowances, 0)
        return sua_due + lua_due + iua_due
