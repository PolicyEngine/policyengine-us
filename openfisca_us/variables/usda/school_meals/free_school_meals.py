from openfisca_us.model_api import *


class free_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Free school meals"
    unit = USD
    documentation = "Value of free school meals"

    def formula(spm_unit, period, parameters):
        tier = spm_unit("school_meal_tier", period).decode_to_str()
        is_free = tier == "FREE"
        return is_free * spm_unit("school_meal_net_subsidy", period)
