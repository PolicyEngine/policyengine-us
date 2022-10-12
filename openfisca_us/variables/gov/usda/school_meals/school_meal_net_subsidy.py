from policyengine_us.model_api import *


class school_meal_net_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Free and reduced price school meals"
    unit = USD
    documentation = "Value of free and reduced price school meal subsidies"

    def formula(spm_unit, period, parameters):
        # Calculate net daily subsidy per child, subtracting the daily subsidy
        # for full-price children.
        daily_subsidy = spm_unit("school_meal_daily_subsidy", period)
        daily_paid_subsidy = spm_unit("school_meal_paid_daily_subsidy", period)
        net_daily_subsidy_per_child = daily_subsidy - daily_paid_subsidy
        # Multiply by number of school days in the year and number of children
        # in school.
        p_school_meals = parameters(period).gov.usda.school_meals
        children = add(spm_unit, period, ["is_in_k12_school"])
        return (
            net_daily_subsidy_per_child * children * p_school_meals.school_days
        )
