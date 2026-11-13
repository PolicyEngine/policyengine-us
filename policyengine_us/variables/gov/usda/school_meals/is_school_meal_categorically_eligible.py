from policyengine_us.model_api import *


def _school_meal_child_categorical_eligibility(person, period, parameters):
    """Return this person's individual school meal categorical eligibility."""
    # Congress qualifies a child whom Head Start enrolls under 42 U.S.C.
    # 9840(a)(1)(B) (42 U.S.C. 1758(b)(12)(A)(iii)). Programs may enroll
    # children above the income limit under 9840(a)(1)(B)(iii), so
    # enrollment qualifies the child here without an income test.
    # Congress also qualifies a foster child whom a title IV-B or IV-E agency
    # or a court has placed (1758(b)(12)(A)(vii)). The monthly input
    # is_in_foster_care stands in for that placement, and one month of it
    # qualifies the child for the year.
    p = parameters(period).gov.usda.school_meals
    return add(person, period, p.child_categorical_eligibility, options=[ADD]) > 0


class is_school_meal_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Categorically eligible for free school meals"
    definition_period = YEAR
    documentation = (
        "Whether this person qualifies through the SPM unit's SNAP, TANF or "
        "FDPIR participation or the household's homelessness, or through their "
        "own Head Start enrollment, foster care, homelessness, migrant status "
        "or runaway status. School meal values also require K-12 attendance."
    )
    reference = (
        "https://uscode.house.gov/us/usc/119-124/t42/s1758/#b-12-A",
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(7)",
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(8)",
    )

    def formula(person, period, parameters):
        household_category = person.spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        return household_category | _school_meal_child_categorical_eligibility(
            person, period, parameters
        )
