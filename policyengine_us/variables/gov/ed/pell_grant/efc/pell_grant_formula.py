from policyengine_us.model_api import *


class SnapUtilityRegion(Enum):
    A = "A"
    B = "B"
    C = "C"


class pell_grant_formula(Variable):
    value_type = Enum
    possible_values = SnapUtilityRegion
    default_value = SnapUtilityRegion.A
    entity = Person
    label = "Formula"
    definition_period = YEAR
