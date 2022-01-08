from openfisca_us.model_api import *


class SchoolMealTier(Enum):
    FREE = "Free"
    REDUCED = "Reduced price"
    PAID = "Paid"


class spm_unit_school_meal_tier(Variable):
    value_type = Enum
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's school meal program tier"

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("spm_unit_school_meal_fpg_ratio", period)
        p_income_limit = parameters(period).usda.school_meals.income_limit
        return select(
            [
                fpg_ratio <= p_income_limit.FREE,
                fpg_ratio <= p_income_limit.REDUCED,
                True,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED, SchoolMealTier.PAID],
        )
