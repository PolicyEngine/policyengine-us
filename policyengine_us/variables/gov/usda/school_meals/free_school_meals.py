from policyengine_us.model_api import *


class free_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Free school meals"
    unit = USD
    documentation = "Value of free school meals"

    def formula(spm_unit, period, parameters):
        disabled_programs = parameters(period).simulation.disabled_programs
        if "free_school_meals" in disabled_programs:
            return spm_unit("free_school_meals_reported", period)
        tier = spm_unit("school_meal_tier", period)
        is_free = tier == tier.possible_values.FREE
        return is_free * spm_unit("school_meal_net_subsidy", period)
