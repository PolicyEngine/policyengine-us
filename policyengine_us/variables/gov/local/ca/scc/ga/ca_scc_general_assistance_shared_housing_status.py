from policyengine_us.model_api import *


class CaSccGeneralAssistanceSharedHousingStatus(Enum):
    SHARED_WITH_ONE = "Shared with one other person"
    SHARED_WITH_TWO = "Shared with two other persons"
    SHARED_WITH_THREE_OR_MORE = "Shared with three or more other persons"
    NOT_SHARED = "Not shared"


class ca_scc_general_assistance_shared_housing_status(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = CaSccGeneralAssistanceSharedHousingStatus
    default_value = CaSccGeneralAssistanceSharedHousingStatus.NOT_SHARED
    definition_period = MONTH
    label = "Santa Clara County General Assistance shared housing status"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/14Payment/Shared_Housing.htm"
