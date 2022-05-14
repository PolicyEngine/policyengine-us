from openfisca_us.model_api import *


class school_meal_daily_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidies per child per day"
    unit = USD
    documentation = "Value of school meal subsidies per child per day"

    def formula(spm_unit, period, parameters):
        # Get state group and tier (based on poverty ratio) for SPM unit.
        state_group = spm_unit.household("state_group_str", period)
        tier = spm_unit("school_meal_tier", period).decode_to_str()
        p_amount = parameters(period).usda.school_meals.amount
        nslp_per_child = p_amount.nslp[state_group][tier]
        sbp_per_child = p_amount.sbp[state_group][tier]
        return nslp_per_child + sbp_per_child
