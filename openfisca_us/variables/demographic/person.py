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
    value_type = int
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


class ccdf_age(Variable):
    value_type = float
    entity = Person
    label = u"CCDF age"
    definition_period = YEAR


class CCDFCareLocation(Enum):
    CENTER_BASED = "Center-based"
    HOME_BASED = "Home-based"


class ccdf_care_location(Variable):
    value_type = Enum
    possible_values = CCDFCareLocation
    default_values = CCDFCareLocation.CENTER_BASED
    entity = Person
    label = u"CCDF care location"
    definition_period = YEAR


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
        ccdf_age = person("ccdf_age", period)
        ccdf_care_location = person(
            "ccdf_care_location", period
        ).decode_to_str()
        return select(
            [
                (ccdf_age < 1.5 and ccdf_care_location == "CENTER_BASED")
                or (ccdf_age < 2 and ccdf_care_location == "HOME_BASED"),
                (ccdf_age < 2 and ccdf_care_location == "CENTER_BASED")
                or (ccdf_age < 3 and ccdf_care_location == "HOME_BASED"),
                ccdf_age < 6,
                ccdf_age < 13,
            ],
            [CCDFAgeGroup.I, CCDFAgeGroup.T, CCDFAgeGroup.PS, CCDFAgeGroup.SA],
        )
