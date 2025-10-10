from policyengine_us.model_api import *


class TXCCSProviderType(Enum):
    LCCC = "Licensed Child Care Center"
    LCCH = "Licensed Child Care Home"
    RCCH = "Registered Child Care Home"
    RELATIVE = "Relative Care"


class tx_ccs_provider_type(Variable):
    value_type = Enum
    possible_values = TXCCSProviderType
    default_value = TXCCSProviderType.LCCC
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) provider type"
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf"
