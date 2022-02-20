from openfisca_us.model_api import *


class school_meal_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Free and reduced price school meals"
    unit = USD
    documentation = "Value of free and reduced price school meal subsidies"

    def formula(spm_unit, period, parameters):
        # Get state group and tier (based on poverty ratio) for SPM unit.
        state_group = spm_unit.household("state_group_str", period)
        tier = spm_unit("school_meal_tier", period).decode_to_str()
        # Get parameters.
        p_school_meals = parameters(period).usda.school_meals
        p_amount = p_school_meals.amount
        # Get NSLP and SBP per child for each SPM unit.
        nslp_per_child = p_amount.nslp[state_group][tier]
        sbp_per_child = p_amount.sbp[state_group][tier]
        # Subtract subsidies that would be paid to full-price children.
        net_daily_subsidy_per_child = (
            nslp_per_child
            + sbp_per_child
            - spm_unit("school_meal_paid_subsidy", period)
        )
        # Multiply by number of school days in the year and number of children
        # in school.
        children = add(spm_unit, period, ["is_in_school"])
        return (
            net_daily_subsidy_per_child * children * p_school_meals.school_days
        )
