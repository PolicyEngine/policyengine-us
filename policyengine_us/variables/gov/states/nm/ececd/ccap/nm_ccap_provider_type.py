from policyengine_us.model_api import *


class NMCCAPProviderType(Enum):
    CENTER = "Licensed Center"
    GROUP_HOME = "Licensed Group Home"
    FAMILY_HOME = "Licensed Family Home"
    REGISTERED_HOME = "Registered Home / In-Home"


class nm_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = NMCCAPProviderType
    default_value = NMCCAPProviderType.CENTER
    definition_period = MONTH
    label = "New Mexico CCAP child care provider type"
    defined_for = StateCode.NM
    reference = "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=2"
