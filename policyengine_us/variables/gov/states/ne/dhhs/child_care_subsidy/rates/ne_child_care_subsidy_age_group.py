from policyengine_us.model_api import *


class NEChildCareSubsidyAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class ne_child_care_subsidy_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NEChildCareSubsidyAgeGroup
    default_value = NEChildCareSubsidyAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy child age group"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=4",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=6",
        "https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.age_group
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        in_school = person("is_in_k12_school", period.this_year)
        return select(
            [
                age_in_months < p.infant_max_months,
                age_in_months < p.toddler_max_months,
                ~in_school,
                in_school,
            ],
            [
                NEChildCareSubsidyAgeGroup.INFANT,
                NEChildCareSubsidyAgeGroup.TODDLER,
                NEChildCareSubsidyAgeGroup.PRESCHOOL,
                NEChildCareSubsidyAgeGroup.SCHOOL_AGE,
            ],
            default=NEChildCareSubsidyAgeGroup.SCHOOL_AGE,
        )
