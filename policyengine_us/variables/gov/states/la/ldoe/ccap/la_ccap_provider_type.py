from policyengine_us.model_api import *


class LACCAPProviderType(Enum):
    TYPE_III_EARLY_LEARNING_CENTER = "Type III early learning center"
    SCHOOL_CHILD_CARE_CENTER = "School child care center"
    FAMILY_CHILD_CARE = "Family child care provider"
    IN_HOME = "In-home provider"
    MILITARY_CHILD_CARE_CENTER = "Military child care center"


class la_ccap_provider_type(Variable):
    value_type = Enum
    possible_values = LACCAPProviderType
    default_value = LACCAPProviderType.TYPE_III_EARLY_LEARNING_CENTER
    entity = Person
    definition_period = YEAR
    label = "Louisiana CCAP child care provider type"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
