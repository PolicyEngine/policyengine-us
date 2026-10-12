from policyengine_us.model_api import *


class NDCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class nd_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NDCCAPAgeGroup
    default_value = NDCCAPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "North Dakota CCAP rate-table age group"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.age_group
        # The rate table is keyed on the HHS web age-group headers: Infant
        # (birth through 17 months), Toddler (18 through 35 months), Preschool
        # (three years through school age), and Other/School age. These
        # boundaries differ slightly from the manual's 400-28-100-30 bands at
        # the infant/toddler and preschool edges; the rate table the rate
        # column is looked up from governs.
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        is_in_school = person("is_in_k12_school", period.this_year)
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                (age_months >= p.preschool_min_months) & ~is_in_school,
            ],
            [
                NDCCAPAgeGroup.INFANT,
                NDCCAPAgeGroup.TODDLER,
                NDCCAPAgeGroup.PRESCHOOL,
            ],
            default=NDCCAPAgeGroup.SCHOOL_AGE,
        )
