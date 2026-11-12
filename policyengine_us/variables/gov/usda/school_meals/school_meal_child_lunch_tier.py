from policyengine_us.model_api import *
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
        "The SPM unit's income and state-policy lunch tier, with free "
        "lunch for this child's own categorical eligibility."
    )
    reference = "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(8)"

    def formula(person, period, parameters):
        tier = person.spm_unit("school_meal_lunch_tier", period)
        categorical = person("is_school_meal_categorically_eligible", period)
        return where(categorical, SchoolMealTier.FREE, tier)
