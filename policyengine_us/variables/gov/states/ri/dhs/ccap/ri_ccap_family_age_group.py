from policyengine_us.model_api import *


class RICCAPFamilyAgeGroup(Enum):
    INFANT_TODDLER = "Infant/Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class ri_ccap_family_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPFamilyAgeGroup
    default_value = RICCAPFamilyAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Rhode Island CCAP licensed family and exempt age group"
    defined_for = StateCode.RI
    reference = (
        "https://dhs.ri.gov/media/7481/download?language=en",
        "https://dhs.ri.gov/media/3556/download?language=en",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.age_group.family
        age = person("age", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        return select(
            [
                age < p.infant_toddler_max,
                ~is_in_school,
            ],
            [
                RICCAPFamilyAgeGroup.INFANT_TODDLER,
                RICCAPFamilyAgeGroup.PRESCHOOL,
            ],
            default=RICCAPFamilyAgeGroup.SCHOOL_AGE,
        )
