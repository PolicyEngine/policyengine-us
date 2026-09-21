from policyengine_us.model_api import *


class MDCCSProviderType(Enum):
    LICENSED_CENTER = "Licensed Child Care Center"
    LICENSED_FAMILY = "Licensed Family Child Care Home"
    INFORMAL = "Informal/License-Exempt"
    NONE = "None"


class md_ccs_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MDCCSProviderType
    # A licensed center, like every other state's provider-type default: the
    # care a reported child-care bill prices, and the rate table's first
    # column. NONE zeroes the payment rate, so as the default it paid an
    # eligible household $0 unless the caller knew to name a provider
    # (policyengine-us #9485).
    default_value = MDCCSProviderType.LICENSED_CENTER
    definition_period = MONTH
    label = "Maryland CCS child care provider type"
    defined_for = StateCode.MD
    reference = "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.11"
