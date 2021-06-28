from openfisca_core.model_api import *
from openfisca_us.entities import *

class MARSType(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HOUSEHOLD_HEAD = "Head of household",
    WIDOW = "Widow(er)"

class MARS(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = MARSType
    default_value = MARSType.SINGLE
    definition_period = YEAR
    label = "MARS Status for the tax unit"