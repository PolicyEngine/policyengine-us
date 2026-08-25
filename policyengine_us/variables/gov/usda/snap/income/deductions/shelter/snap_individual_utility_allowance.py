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

        # HI and GU vary electricity, gas, and water by household size
        hh_size_states = utility.single.by_household_size.states
        is_hh_size_state = is_in(region, hh_size_states)
        spm_size = spm_unit("spm_unit_size", period)
        MAX_SPM_SIZE = 10
        capped_size = max_(1, min_(MAX_SPM_SIZE, spm_size))
        # Use HI as safe default key for non-HH-size states
        safe_region = where(is_hh_size_state, region, "HI")

        hh_size_utilities = {"electricity", "gas_and_fuel", "water"}
        # Households receive an individual standard only for each utility
        # expense they actually incur (7 CFR 273.9(d)(6)(iii)(A)).
        # Use pre-subsidy electricity expenses to avoid circular references
        # since electricity subsidies depend on SNAP enrollment.
        expense_variables = {
            "electricity": "pre_subsidy_electricity_expense",
            "gas_and_fuel": "gas_expense",
            "water": "water_expense",
            "sewage": "sewage_expense",
            "phone": "phone_expense",
            "trash": "trash_expense",
        }

        sum_of_individual_allowances = 0
        for expense in expense_types:
            util_name = expense.replace("_expense", "")
            incurs_expense = spm_unit(expense_variables[util_name], period) > 0
            flat_val = utility.single[util_name][region]
            if util_name in hh_size_utilities:
                hh_val = utility.single.by_household_size[util_name][safe_region][
                    capped_size
                ]
                allowance = where(is_hh_size_state, hh_val, flat_val)
            else:
                allowance = flat_val
            sum_of_individual_allowances += incurs_expense * allowance

        return where(
            allowance_type == allowance_types.IUA,
            sum_of_individual_allowances,
            0,
        )
