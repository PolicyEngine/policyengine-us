from policyengine_us.model_api import *


def school_meal_values_above_paid(
    spm_unit, period, parameters, breakfast_tier, lunch_tier
):
    """Return the per-child daily value of breakfast and lunch above the
    paid rate at the given tiers.
    """
    state_group = spm_unit.household("state_group_str", period)
    p_amount = parameters(period).gov.usda.school_meals.amount
    breakfast_value = (
        p_amount.sbp[state_group][breakfast_tier.decode_to_str()]
        - p_amount.sbp[state_group]["PAID"]
    )
    lunch_value = (
        p_amount.nslp[state_group][lunch_tier.decode_to_str()]
        - p_amount.nslp[state_group]["PAID"]
    )
    return breakfast_value, lunch_value


def school_meal_share_of_year_without_categorical_eligibility(spm_unit, period):
    """Return the share of the year before categorical eligibility starts,
    or zero without categorical eligibility.
    """
    months = spm_unit("school_meal_categorical_eligibility_months", period)
    return where(months > 0, 1 - months / MONTHS_IN_YEAR, 0)


class school_meal_daily_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidies per child per day"
    unit = USD
    documentation = (
        "Value of school meal subsidies per child per day, as a yearly "
        "average: the School Breakfast Program rate at the breakfast tier plus "
        "the National School Lunch Program rate at the lunch tier. Months "
        "before categorical eligibility starts count at the tiers without it."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1773#e_1_A",
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
        "https://www.law.cornell.edu/cfr/text/7/245.6#c_1",
    )

    def formula(spm_unit, period, parameters):
        state_group = spm_unit.household("state_group_str", period)
        p_amount = parameters(period).gov.usda.school_meals.amount

        def daily_subsidy(breakfast_tier, lunch_tier):
            return (
                p_amount.nslp[state_group][lunch_tier.decode_to_str()]
                + p_amount.sbp[state_group][breakfast_tier.decode_to_str()]
            )

        subsidy = daily_subsidy(
            spm_unit("school_meal_breakfast_tier", period),
            spm_unit("school_meal_lunch_tier", period),
        )
        subsidy_without_categorical = daily_subsidy(
            spm_unit(
                "school_meal_breakfast_tier_without_categorical_eligibility", period
            ),
            spm_unit("school_meal_lunch_tier_without_categorical_eligibility", period),
        )
        share_without = school_meal_share_of_year_without_categorical_eligibility(
            spm_unit, period
        )
        return subsidy + share_without * (subsidy_without_categorical - subsidy)
