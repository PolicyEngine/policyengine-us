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
        p_income_limit = parameters(period).gov.usda.school_meals.income.limit
        # Categorical eligibility provides free school meals.
        categorical_eligibility = spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        return select(
            [
                (fpg_ratio <= p_income_limit.FREE) | categorical_eligibility,
                fpg_ratio <= p_income_limit.REDUCED,
                True,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED, SchoolMealTier.PAID],
        )
