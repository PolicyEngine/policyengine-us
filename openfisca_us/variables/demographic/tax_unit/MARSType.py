from openfisca_us.model_api import *


class MARSType(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HOUSEHOLD_HEAD = "Head of household"
    WIDOW = "Widow(er)"
