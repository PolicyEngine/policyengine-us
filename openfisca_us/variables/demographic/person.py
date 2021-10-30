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


class ProviderType(Enum):
    DCC_SACC = "Licenced/registered/permitted day care center; registered school-age child care"
    FDC_GFDC = "Registered family day care homes; licensed group family day care"
    LE_GC = "Legally exempt group child care programs"
    LE_STD = "Informal child care standard rate"
    LE_ENH = "Informal child care enhanced rate"


class provider_type(Variable):
    value_type = Enum
    possible_values = ProviderType
    default_value = ProviderType.DCC_SACC
    entity = Person
    label = u"ProviderType"
    definition_period = YEAR
    # DCC_SACC is most common among provider types
