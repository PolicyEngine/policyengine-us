from policyengine_us.model_api import *


def _school_meal_child_categorical_eligibility(person, period):
    """Return this person's individual school meal categorical eligibility."""
    # Enrollment qualifies the participant, including an enrollee whose
    # income exceeds the modeled Head Start income limit (USDA SP 40-2013).
    head_start = person("is_enrolled_in_head_start", period)
    foster = person("is_in_foster_care", period, options=[ADD]) > 0
    homeless = person("is_homeless_child", period) | person.household(
        "is_homeless", period
    )
    return (
        head_start
        | foster
        | homeless
        | person("is_migratory_child", period)
        | person("is_runaway_child", period)
    )


class is_school_meal_categorically_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Categorically eligible for free school meals"
    definition_period = YEAR
    documentation = (
        "Whether this person qualifies through the SPM unit's SNAP, TANF or "
        "FDPIR participation, or their own Head Start enrollment, foster care, "
        "homelessness, migrant status or runaway status. School meal values "
        "also require K-12 attendance."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_12_A",
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(7)",
        "https://www.ecfr.gov/current/title-7/section-245.6#p-245.6(b)(8)",
    )

    def formula(person, period, parameters):
        household_category = person.spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        return household_category | _school_meal_child_categorical_eligibility(
            person, period
        )
