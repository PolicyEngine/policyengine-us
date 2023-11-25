from policyengine_us.model_api import *


class ImmigrationStatusStr(Enum):
    CITIZEN = "CITIZEN"
    RESIDENT = "RESIDENT"
    DACA_TPS = "DACA_TPS"
    UNDOCUMENTED = "UNDOCUMENTED"


class immigration_status_str(Variable):
    value_type = Enum
    possible_values = ImmigrationStatusStr
    default_value = ImmigrationStatusStr.CITIZEN
    entity = Person
    label = "Immigration status as an all-upper-case string"
    definition_period = YEAR
