from policyengine_us.model_api import *


class NMCCAPFocusLevel(Enum):
    TWO_STAR = "2-Star"
    TWO_PLUS_STAR = "2+Star FOCUS"
    THREE_STAR = "3-Star FOCUS"
    FOUR_STAR = "4-Star FOCUS"
    FIVE_STAR = "5-Star FOCUS"


class nm_ccap_focus_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = NMCCAPFocusLevel
    default_value = NMCCAPFocusLevel.TWO_STAR
    definition_period = MONTH
    label = "New Mexico CCAP provider FOCUS quality level"
    defined_for = StateCode.NM
    reference = "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=2"
