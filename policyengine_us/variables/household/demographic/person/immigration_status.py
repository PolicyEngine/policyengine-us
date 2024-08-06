from policyengine_us.model_api import *


class ImmigrationStatus(Enum):
    CITIZEN = "Citizen"
    LEGAL_PERMANENT_RESIDENT = "Legal Permanent Resident"
    REFUGEE = "Refugee"
    ASYLEE = "Asylee"
    DEPORTATION_WITHHELD = "Deportation Withheld"
    CUBAN_HAITIAN_ENTRANT = "Cuban/Haitian Entrant"
    CONDITIONAL_ENTRANT = "Conditional Entrant"
    PAROLED_ONE_YEAR = "Paroled for at Least One Year"
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
        status_str = person("immigration_status_str", period).decode_to_str()
        # Use PolicyEngine's Enum encode method
        return ImmigrationStatus.encode(status_str)
