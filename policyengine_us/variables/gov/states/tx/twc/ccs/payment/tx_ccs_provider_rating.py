from policyengine_us.model_api import *


class TXCCSProviderRating(Enum):
    REG = "Regular"
    TRS2 = "Texas Rising Star 2"
    TRS3 = "Texas Rising Star 3"
    TRS4 = "Texas Rising Star 4"
    TSR = "Texas School Ready"
    NONE = "None"


class tx_ccs_provider_rating(Variable):
    value_type = Enum
    possible_values = TXCCSProviderRating
    default_value = TXCCSProviderRating.REG
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) provider rating"
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf"
