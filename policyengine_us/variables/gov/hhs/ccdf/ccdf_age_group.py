from policyengine_us.model_api import *


class CCDFAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOLER = "Preschooler"
    SCHOOL_AGE = "School age"


class ccdf_age_group(Variable):
    value_type = Enum
    possible_values = CCDFAgeGroup
    default_value = CCDFAgeGroup.INFANT
    entity = Person
    label = "CCDF age group"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf"

    def formula(person, period, parameters):
        age = person("age", period)
        home_based = person("is_ccdf_home_based", period)
        return select(
            [
                ((age < 2) & ~home_based) | ((age < 3) & home_based),
                age < 6,
                age < 13,
            ],
            [
                CCDFAgeGroup.TODDLER,
                CCDFAgeGroup.PRESCHOOLER,
                CCDFAgeGroup.SCHOOL_AGE,
            ],
            # Default covers INFANT: (age < 1.5 & ~home_based) | (age < 2 & home_based)
            # as well as ages 13+
            default=CCDFAgeGroup.INFANT,
        )
