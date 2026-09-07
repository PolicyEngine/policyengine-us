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

    reference = (
        "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf"
    )

    def formula(person, period, parameters):
        age = person("age", period)
        home_based = person("is_ccdf_home_based", period)
        # Every person in the simulation gets an age group, including adults.
        # Without an explicit default, numpy's select fills unmatched rows
        # (age >= 13) with the integer 0, which cannot be encoded as a
        # CCDFAgeGroup. Anyone past the school-age bracket stays SCHOOL_AGE;
        # is_ccdf_age_eligible screens them out of the subsidy.
        return select(
            [
                ((age < 1.5) & ~home_based) | ((age < 2) & home_based),
                ((age < 2) & ~home_based) | ((age < 3) & home_based),
                age < 6,
            ],
            [
                CCDFAgeGroup.INFANT,
                CCDFAgeGroup.TODDLER,
                CCDFAgeGroup.PRESCHOOLER,
            ],
            default=CCDFAgeGroup.SCHOOL_AGE,
        )
