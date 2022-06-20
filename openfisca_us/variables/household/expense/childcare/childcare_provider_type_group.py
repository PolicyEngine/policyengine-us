from openfisca_us.model_api import *


class ChildcareProviderTypeGroup(Enum):
    DCC_SACC = "Licenced/registered/permitted day care center; registered school-age child care"
    FDC_GFDC = (
        "Registered family day care homes; licensed group family day care"
    )
    LE_GC = "Legally exempt group child care programs"
    LE_STD = "Informal child care standard rate"
    LE_ENH = "Informal child care enhanced rate"


class childcare_provider_type_group(Variable):
    value_type = Enum
    possible_values = ChildcareProviderTypeGroup
    # DCC_SACC is most common among provider types
    default_value = ChildcareProviderTypeGroup.DCC_SACC
    entity = Person
    label = "Childcare provider type group"
    definition_period = YEAR
