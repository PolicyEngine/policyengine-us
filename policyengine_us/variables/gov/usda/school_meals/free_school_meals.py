from policyengine_us.model_api import *


class free_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "free school meals"
    unit = USD
    documentation = (
        "Modeled value of meals with no family charge, including state-paid "
        "reduced-price copays. This is not a count of federally certified "
        "free-meal students or an estimate of state spending."
    )

    def formula(spm_unit, period, parameters):
        tier = spm_unit("school_meal_tier", period)
        is_free = tier == tier.possible_values.FREE
        return is_free * spm_unit("school_meal_net_subsidy", period)
