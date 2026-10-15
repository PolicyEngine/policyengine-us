from policyengine_us.model_api import *


class school_meal_daily_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidies per child per day"
    unit = USD
    documentation = (
        "Value of school meal subsidies per child per day: the School Breakfast "
        "Program rate at the breakfast tier plus the National School Lunch "
        "Program rate at the lunch tier."
    )

    def formula(spm_unit, period, parameters):
        # Get state group and per-meal tiers for SPM unit.
        state_group = spm_unit.household("state_group_str", period)
        breakfast_tier = spm_unit("school_meal_breakfast_tier", period).decode_to_str()
        lunch_tier = spm_unit("school_meal_lunch_tier", period).decode_to_str()
        p_amount = parameters(period).gov.usda.school_meals.amount
        nslp_per_child = p_amount.nslp[state_group][lunch_tier]
        sbp_per_child = p_amount.sbp[state_group][breakfast_tier]
        return nslp_per_child + sbp_per_child
