from openfisca_us.model_api import *


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
                ((age < 1.5) & ~home_based) | ((age < 2) & home_based),
                ((age < 2) & ~home_based) | ((age < 3) & home_based),
                age < 6,
                age < 13,
            ],
            [
                CCDFAgeGroup.INFANT,
                CCDFAgeGroup.TODDLER,
                CCDFAgeGroup.PRESCHOOLER,
                CCDFAgeGroup.SCHOOL_AGE,
            ],
        )
