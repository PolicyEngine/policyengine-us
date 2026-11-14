from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_daily_subsidy import (
    school_meal_daily_rate,
)


class reduced_price_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "reduced price school meals"
    unit = USD
    documentation = (
        "Value of school meals served at the reduced price. When a state "
        "policy makes only breakfast or only lunch free, the other meal's "
        "value stays here."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # Weight each school child's reduced-price meals by their net value.
        reduced_value = school_meal_daily_rate(
            spm_unit, period, parameters, net=True, tier="REDUCED"
        )
        total_value = school_meal_daily_rate(spm_unit, period, parameters, net=True)
        reduced_share = np.divide(
            reduced_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return reduced_share * spm_unit("school_meal_net_subsidy", period)
