from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)


class immigration_status_str(Variable):
    value_type = Enum
    possible_values = ImmigrationStatus
    default_value = ImmigrationStatus.CITIZEN
    entity = Person
    label = "ImmigrationStatus enumeration type as an all-upper-case string"
    definition_period = YEAR
