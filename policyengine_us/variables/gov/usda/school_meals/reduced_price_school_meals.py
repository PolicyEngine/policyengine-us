from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_daily_subsidy import (
    school_meal_share_of_year_without_categorical_eligibility,
    school_meal_values_above_paid,
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
        "value stays here. Months before categorical eligibility starts "
        "count at the tiers without it."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # Split the net subsidy by each meal's value above the paid rate, so
        # each meal counts here only when its own tier is REDUCED. Months
        # before categorical eligibility starts count at the tiers without it.
        def reduced_and_total_values(breakfast_tier, lunch_tier):
            breakfast_value, lunch_value = school_meal_values_above_paid(
                spm_unit, period, parameters, breakfast_tier, lunch_tier
            )
            reduced_breakfast = breakfast_tier == breakfast_tier.possible_values.REDUCED
            reduced_lunch = lunch_tier == lunch_tier.possible_values.REDUCED
            reduced_value = where(reduced_breakfast, breakfast_value, 0) + where(
                reduced_lunch, lunch_value, 0
            )
            return reduced_value, breakfast_value + lunch_value

        reduced_value, total_value = reduced_and_total_values(
            spm_unit("school_meal_breakfast_tier", period),
            spm_unit("school_meal_lunch_tier", period),
        )
        reduced_value_without, total_value_without = reduced_and_total_values(
            spm_unit(
                "school_meal_breakfast_tier_without_categorical_eligibility", period
            ),
            spm_unit("school_meal_lunch_tier_without_categorical_eligibility", period),
        )
        share_without = school_meal_share_of_year_without_categorical_eligibility(
            spm_unit, period
        )
        reduced_value = reduced_value + share_without * (
            reduced_value_without - reduced_value
        )
        total_value = total_value + share_without * (total_value_without - total_value)
        reduced_share = np.divide(
            reduced_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return reduced_share * spm_unit("school_meal_net_subsidy", period)
