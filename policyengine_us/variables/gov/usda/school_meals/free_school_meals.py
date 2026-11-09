from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_daily_subsidy import (
    school_meal_share_of_year_without_categorical_eligibility,
    school_meal_values_above_paid,
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
        "certified free-meal students or an estimate of state spending. "
        "Months before categorical eligibility starts count at the tiers "
        "without it."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # Split the net subsidy by each meal's value above the paid rate, so
        # each meal counts here only when its own tier is FREE. Months
        # before categorical eligibility starts count at the tiers without it.
        def free_and_total_values(breakfast_tier, lunch_tier):
            breakfast_value, lunch_value = school_meal_values_above_paid(
                spm_unit, period, parameters, breakfast_tier, lunch_tier
            )
            free_breakfast = breakfast_tier == breakfast_tier.possible_values.FREE
            free_lunch = lunch_tier == lunch_tier.possible_values.FREE
            free_value = where(free_breakfast, breakfast_value, 0) + where(
                free_lunch, lunch_value, 0
            )
            return free_value, breakfast_value + lunch_value

        free_value, total_value = free_and_total_values(
            spm_unit("school_meal_breakfast_tier", period),
            spm_unit("school_meal_lunch_tier", period),
        )
        free_value_without, total_value_without = free_and_total_values(
            spm_unit(
                "school_meal_breakfast_tier_without_categorical_eligibility", period
            ),
            spm_unit("school_meal_lunch_tier_without_categorical_eligibility", period),
        )
        share_without = school_meal_share_of_year_without_categorical_eligibility(
            spm_unit, period
        )
        free_value = free_value + share_without * (free_value_without - free_value)
        total_value = total_value + share_without * (total_value_without - total_value)
        free_share = np.divide(
            free_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return free_share * spm_unit("school_meal_net_subsidy", period)
