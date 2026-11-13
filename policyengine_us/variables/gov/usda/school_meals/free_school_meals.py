from policyengine_us.model_api import *


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
        # Split the net subsidy by each meal's value above the paid rate, so
        # each meal counts here only when its own tier is FREE.
        state_group = spm_unit.household("state_group_str", period)
        breakfast_tier = spm_unit("school_meal_breakfast_tier", period)
        lunch_tier = spm_unit("school_meal_lunch_tier", period)
        p_amount = parameters(period).gov.usda.school_meals.amount
        breakfast_value = (
            p_amount.sbp[state_group][breakfast_tier.decode_to_str()]
            - p_amount.sbp[state_group]["PAID"]
        )
        lunch_value = (
            p_amount.nslp[state_group][lunch_tier.decode_to_str()]
            - p_amount.nslp[state_group]["PAID"]
        )
        free_breakfast = breakfast_tier == breakfast_tier.possible_values.FREE
        free_lunch = lunch_tier == lunch_tier.possible_values.FREE
        free_value = where(free_breakfast, breakfast_value, 0) + where(
            free_lunch, lunch_value, 0
        )
        total_value = breakfast_value + lunch_value
        free_share = np.divide(
            free_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return free_share * spm_unit("school_meal_net_subsidy", period)
