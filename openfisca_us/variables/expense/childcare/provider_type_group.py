from openfisca_us.model_api import *


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
    label = u"Childcare provider type group"
    definition_period = YEAR
