from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.is_school_meal_categorically_eligible import (
    _school_meal_child_categorical_eligibility,
)
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
)


class school_meal_child_lunch_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    label = "School lunch tier for this child"
    definition_period = YEAR
    documentation = (
        "The SPM unit's lunch tier, including household categorical "
        "eligibility, with free lunch for this child's own categorical "
        "eligibility. Explicit SPM-unit tier inputs apply to children "
        "without an individual category."
    )
    reference = "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(8)"

    def formula(person, period, parameters):
        tier = person.spm_unit("school_meal_lunch_tier", period)
        categorical = _school_meal_child_categorical_eligibility(
            person, period, parameters
        )
        return where(categorical, SchoolMealTier.FREE.index, tier)
