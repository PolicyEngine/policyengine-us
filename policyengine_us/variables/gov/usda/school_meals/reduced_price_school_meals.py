from policyengine_us.model_api import *


class reduced_price_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Reduced price school meals"
    unit = USD
    documentation = "Value of reduced price school meals"

    def formula(spm_unit, period, parameters):
        tier = spm_unit("school_meal_tier", period)
        is_reduced_price = tier == tier.possible_values.REDUCED
        return is_reduced_price * spm_unit("school_meal_net_subsidy", period)
