from policyengine_us.model_api import *


class MOCCSProviderType(Enum):
    REGISTERED_CENTER = "Registered child care center"
    SIX_OR_FEWER = "License-exempt provider caring for six or fewer children"
    LICENSED_CENTER = "Licensed child care center"
    LICENSED_FAMILY_HOME = "Licensed family child care home"
    GROUP_HOME = "Licensed group child care home"


class mo_ccs_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MOCCSProviderType
    default_value = MOCCSProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Missouri Child Care Subsidy provider type"
    defined_for = StateCode.MO
    reference = "https://dese.mo.gov/sites/dese/files/media/file/2025/12/2025%20Rates%20Held%20Harmless%202.0.xlsx"
