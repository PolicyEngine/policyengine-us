from policyengine_us.model_api import *


class meets_school_meal_categorical_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household-wide school meal categorical eligibility"
    documentation = (
        "Whether SNAP, TANF or FDPIR participation, or the household's lack of "
        "a fixed nighttime residence, qualifies every child in this SPM unit. "
        "Child-specific categories also apply through "
        "is_school_meal_categorically_eligible."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(7)",
        "https://uscode.house.gov/us/usc/119-124/t42/s1758/#b-12-A",
    )
    adds = "gov.usda.school_meals.categorical_eligibility"
