from policyengine_us.model_api import *


class WAECEAPSlotType(Enum):
    PART_DAY = "Part Day"
    SCHOOL_DAY = "School Day"
    WORKING_DAY = "Working Day"


class wa_eceap_slot_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAECEAPSlotType
    default_value = WAECEAPSlotType.SCHOOL_DAY
    definition_period = YEAR
    defined_for = StateCode.WA
    label = "Washington ECEAP slot type"
    reference = "https://www.dcyf.wa.gov/services/early-learning-providers/eceap/community-funded-eceap/funding"
