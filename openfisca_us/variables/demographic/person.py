from openfisca_core.model_api import *
from openfisca_us.entities import *


class person_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for this person"
    definition_period = ETERNITY


class person_weight(Variable):
    value_type = float
    entity = Person
    label = u"Person weight"
    definition_period = YEAR


class age(Variable):
    value_type = float
    entity = Person
    label = u"Age"
    definition_period = YEAR


class AgeGroup(Enum):
    CHILD = "Child"
    WORKING_AGE = "Working-age"
    SENIOR = "Senior"


class age_group(Variable):
    value_type = Enum
    possible_values = AgeGroup
    default_value = AgeGroup.WORKING_AGE
    entity = Person
    label = u"Age group"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        return select(
            [age < 18, age < 65, age >= 65],
            [AgeGroup.CHILD, AgeGroup.WORKING_AGE, AgeGroup.SENIOR],
        )


class is_ccdf_home_based(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = u"is ccdf home based"
    definition_period = YEAR

    def formula(person, period, parameters):
        provider_type_group = person("provider_type_group", period)
        return provider_type_group != "DCC_SACC"


class CCDFAgeGroup(Enum):
    I = "Infant"
    T = "Toddler"
    PS = "Preschooler"
    SA = "School age"


class ccdf_age_group(Variable):
    value_type = Enum
    possible_values = CCDFAgeGroup
    default_value = CCDFAgeGroup.I
    entity = Person
    label = u"CCDF age group"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        care_location_is_home_based = person(
            "is_ccdf_home_based", period, parameters
        )
        return select(
            [
                (age < 1.5 & ~care_location_is_home_based)
                | (age < 2 & care_location_is_home_based),
                (age < 2 & ~care_location_is_home_based)
                | (age < 3 & care_location_is_home_based),
                age < 6,
                age < 13,
            ],
            [CCDFAgeGroup.I, CCDFAgeGroup.T, CCDFAgeGroup.PS, CCDFAgeGroup.SA],
        )


# Reference for CCDF age group
# https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf


class ProviderTypeGroup(Enum):
    DCC_SACC = "Licenced/registered/permitted day care center; registered school-age child care"
    FDC_GFDC = (
        "Registered family day care homes; licensed group family day care"
    )
    LE_GC = "Legally exempt group child care programs"
    LE_STD = "Informal child care standard rate"
    LE_ENH = "Informal child care enhanced rate"


class provider_type_group(Variable):
    value_type = Enum
    possible_values = ProviderTypeGroup
    # DCC_SACC is most common among provider types
    default_value = ProviderTypeGroup.DCC_SACC
    entity = Person
    label = u"CCDF provider type group"
    definition_period = YEAR
