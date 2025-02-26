from policyengine_us.model_api import *


class MassachusettsEAEDCLivingArrangement(Enum):
    A = "A"  # Living Arrangement A
    B = "B"  # Living Arrangement B
    C = "C"  # Living Arrangement C
    D = "D"  # Living Arrangement D
    E = "E"  # Living Arrangement E
    F = "F"  # Living Arrangement F
    H = "H"  # Living Arrangement H
    NONE = "None"


class ma_eaedc_living_arrangement(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MassachusettsEAEDCLivingArrangement
    default_value = MassachusettsEAEDCLivingArrangement.NONE
    definition_period = YEAR
    label = "Massachusetts EAEDC living arrangement"
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/lists/emergency-aid-to-the-elderly-disabled-and-children-eaedc-grant-calculation"
