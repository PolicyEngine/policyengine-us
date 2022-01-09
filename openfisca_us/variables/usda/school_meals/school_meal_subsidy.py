from openfisca_us.model_api import *


class school_meal_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidy"
    unit = USD
    documentation = "Total school meal subsidy entitlement"

    def formula(spm_unit, period, parameters):
        # Get state group and tier (based on poverty ratio) for SPM unit.
        state_group = spm_unit.household("state_group_str", period)
        tier = spm_unit("spm_unit_school_meal_tier", period).decode_to_str()
        # Get parameters.
        p_school_meals = parameters(period).usda.school_meals
        p_amount = p_school_meals.amount
        # Get NSLP and SBP per child for each SPM unit.
        nslp_per_child = p_amount.nslp[state_group][tier]
        sbp_per_child = p_amount.sbp[state_group][tier]
        # Add NSLP and SBP.
        school_meal_subsidy_per_child = nslp_per_child + sbp_per_child
        # Multiply by number of school days in the year and number of children.
        children = spm_unit.sum(spm_unit.members("age", period) < 18)
        return (
            school_meal_subsidy_per_child
            * children
            * p_school_meals.school_days
        )
