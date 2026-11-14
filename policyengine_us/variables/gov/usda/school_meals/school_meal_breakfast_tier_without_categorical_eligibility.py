from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
)
from policyengine_us.variables.gov.usda.school_meals.school_meal_breakfast_tier import (
    school_meal_breakfast_tier_from,
)


class school_meal_breakfast_tier_without_categorical_eligibility(Variable):
    value_type = Enum
    label = "School breakfast tier without categorical eligibility"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier for breakfast in the months before categorical "
        "eligibility starts. It applies school_meal_breakfast_tier's rules to "
        "school_meal_tier_without_categorical_eligibility."
    )
    reference = "https://www.law.cornell.edu/cfr/text/7/245.6#c_1"

    def formula(spm_unit, period, parameters):
        tier = spm_unit("school_meal_tier_without_categorical_eligibility", period)
        return school_meal_breakfast_tier_from(spm_unit, period, parameters, tier)
