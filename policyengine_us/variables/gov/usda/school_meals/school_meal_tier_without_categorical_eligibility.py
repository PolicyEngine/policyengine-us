from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
    school_meal_tier_from,
)


class school_meal_tier_without_categorical_eligibility(Variable):
    value_type = Enum
    label = "School meal tier without categorical eligibility"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier for both meals from income and state policy alone, "
        "as in school_meal_tier but without categorical eligibility. It "
        "applies in the months before categorical eligibility starts."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.6#c_1",
    )

    def formula(spm_unit, period, parameters):
        return school_meal_tier_from(spm_unit, period, parameters, False)
