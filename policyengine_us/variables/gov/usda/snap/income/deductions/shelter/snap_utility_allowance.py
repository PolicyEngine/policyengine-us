from policyengine_us.model_api import *


class snap_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Standard Utility Allowance"
    unit = USD
    documentation = "The regular utility allowance deduction for SNAP"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        utility = parameters(period).gov.usda.snap.income.deductions.utility
        allowance_type = spm_unit("snap_utility_allowance_type", period)
        allowance_types = allowance_type.possible_values
        region = spm_unit.household("snap_utility_region_str", period)
        sua_due = where(
            allowance_type == allowance_types.SUA, utility.standard[region], 0
        )
        lua_due = where(
            allowance_type == allowance_types.LUA,
            utility.limited.allowance[region],
            0,
        )
        # Make sure that only the subsidy amount which corresponds to the
        # utility expense is included in the individual subsidies
        electricty_subsidy = where(
            spm_unit("electricity_expense", period) > 0,
            utility.single.electricity[region],
            0,
        )
        gas_subsidy = where(
            spm_unit("gas_expense", period) > 0,
            utility.single.gas_and_fuel[region],
            0,
        )
        phone_subsidy = where(
            spm_unit("phone_expense", period) > 0,
            utility.single.phone[region],
            0,
        )
        trash_subsidy = where(
            spm_unit("trash_expense", period) > 0,
            utility.single.trash[region],
            0,
        )
        water_subsidy = where(
            spm_unit("water_expense", period) > 0,
            utility.single.water[region],
            0,
        )
        sewage_subsidy = where(
            spm_unit("sewage_expense", period) > 0,
            utility.single.sewage[region],
            0,
        )
        total_subsidies = (
            electricty_subsidy
            + gas_subsidy
            + phone_subsidy
            + trash_subsidy
            + water_subsidy
            + sewage_subsidy
        )
        iua_due = where(
            allowance_type == allowance_types.IUA,
            total_subsidies,
            0,
        )
        return sua_due + lua_due + iua_due
