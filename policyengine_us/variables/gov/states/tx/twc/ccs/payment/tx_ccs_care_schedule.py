from policyengine_us.model_api import *


class TXCCSCareSchedule(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    BLENDED = "Blended"


class tx_ccs_care_schedule(Variable):
    value_type = Enum
    possible_values = TXCCSCareSchedule
    default_value = TXCCSCareSchedule.FULL_TIME
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) care schedule"
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf"
