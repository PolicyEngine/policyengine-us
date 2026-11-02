from policyengine_us.model_api import *


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
        # Split the net subsidy by each meal's value above the paid rate, so
        # each meal counts here only when its own tier is REDUCED.
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
        reduced_breakfast = breakfast_tier == breakfast_tier.possible_values.REDUCED
        reduced_lunch = lunch_tier == lunch_tier.possible_values.REDUCED
        reduced_value = where(reduced_breakfast, breakfast_value, 0) + where(
            reduced_lunch, lunch_value, 0
        )
        total_value = breakfast_value + lunch_value
        reduced_share = np.divide(
            reduced_value,
            total_value,
            out=np.zeros_like(total_value),
            where=total_value > 0,
        )
        return reduced_share * spm_unit("school_meal_net_subsidy", period)
