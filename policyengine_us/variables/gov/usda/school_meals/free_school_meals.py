from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_daily_subsidy import (
    school_meal_daily_rate,
)


class free_school_meals(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "free school meals"
    unit = USD
    documentation = (
        "Modeled value of meals with no family charge, including state-paid "
        "reduced-price copays and meals made free by state policies that "
        "cover only breakfast or only lunch. This is not a count of federally "
        "certified free-meal students or an estimate of state spending."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # Weight each school child's free meals by their value above paid.
        free_value = school_meal_daily_rate(
            spm_unit, period, parameters, net=True, tier="FREE"
        )
        total_value = school_meal_daily_rate(spm_unit, period, parameters, net=True)
        free_share = np.divide(
            free_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return free_share * spm_unit("school_meal_net_subsidy", period)
