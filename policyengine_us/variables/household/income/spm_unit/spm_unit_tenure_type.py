from policyengine_us.model_api import *


class SPMUnitTenureType(Enum):
    OWNER_WITH_MORTGAGE = "owner with mortgage"
    OWNER_WITHOUT_MORTGAGE = "owner without mortgage"
    RENTER = "renter"


class spm_unit_tenure_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = SPMUnitTenureType
    default_value = SPMUnitTenureType.RENTER
    label = "SPM unit tenure type"
    documentation = "Maps to Census SPM_TENMORTSTATUS codes: 1=owner with mortgage, 2=owner without mortgage, 3=renter"
    definition_period = YEAR
