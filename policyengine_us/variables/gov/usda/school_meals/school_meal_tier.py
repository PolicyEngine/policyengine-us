from policyengine_us.model_api import *


class SchoolMealTier(Enum):
    FREE = "Free"
    REDUCED = "Reduced price"
    PAID = "Paid"


class school_meal_tier(Variable):
    value_type = Enum
    label = "School meal tier"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's school meal program tier"

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        p = parameters(period).gov.usda.school_meals
        p_income_limit = p.income.limit
        # Categorical eligibility provides free school meals.
        categorical_eligibility = spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        # States with universal free meal policies provide the free tier
        # to all students regardless of household income.
        state_universal = spm_unit("state_has_universal_free_school_meals", period)
        # States that cover the reduced-price copay provide the free tier
        # to students who qualify for reduced-price meals.
        reduced_income_eligible = fpg_ratio <= p_income_limit.REDUCED
        state = spm_unit.household("state_code_str", period)
        state_covers_reduced_copay = p.state_covers_reduced_price_copay[state]
        return select(
            [
                (fpg_ratio <= p_income_limit.FREE)
                | categorical_eligibility
                | state_universal
                | (reduced_income_eligible & state_covers_reduced_copay),
                reduced_income_eligible,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
