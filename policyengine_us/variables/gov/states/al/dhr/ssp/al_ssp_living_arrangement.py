from policyengine_us.model_api import *


class ALSSPLivingArrangement(Enum):
    FCMP_NURSING_CARE = "FCMP Nursing Care"
    NURSING_CARE = "Nursing Care Supplement"
    IHC_LEVEL_A = "Independent Homelife Care, Level A"
    IHC_LEVEL_B = "Independent Homelife Care, Level B"
    FOSTER_CARE = "Foster Home Care"
    CEREBRAL_PALSY = "Cerebral Palsy Treatment Center"
    NONE = "Not in a qualifying care arrangement"


class al_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Alabama SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.AL
    possible_values = ALSSPLivingArrangement
    default_value = ALSSPLivingArrangement.NONE
    reference = (
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=10",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=14",
    )
