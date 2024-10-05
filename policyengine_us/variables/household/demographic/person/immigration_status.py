from policyengine_us.model_api import *


class ImmigrationStatus(Enum):
    CITIZEN = "Citizen"
    LEGAL_PERMANENT_RESIDENT = "Legal Permanent Resident"
    DACA_TPS = (
        "Deferred Action for Childhood Arrivals or Temporary Protected Status"
    )
    UNDOCUMENTED = "Undocumented"


class immigration_status(Variable):
    value_type = Enum
    entity = Person
    possible_values = ImmigrationStatus
    default_value = ImmigrationStatus.CITIZEN
    definition_period = YEAR
    label = "U.S. immigration status as an enumeration type"

    def formula(person, period, parameters):
        return ImmigrationStatus.encode(
            person("immigration_status_str", period).decode_to_str()
        )
