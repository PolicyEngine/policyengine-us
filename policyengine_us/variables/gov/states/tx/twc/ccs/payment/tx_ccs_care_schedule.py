from policyengine_us.model_api import *


class TXCCSCareSchedule(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    BLENDED = "Blended"
    UNSPECIFIED = "Unspecified"


class tx_ccs_care_schedule(Variable):
    value_type = Enum
    possible_values = TXCCSCareSchedule
    # Preserve an omitted authorization separately from an explicit full-time
    # authorization, including when only some people supply this input.
    default_value = TXCCSCareSchedule.UNSPECIFIED
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) supplied care schedule"
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf"
