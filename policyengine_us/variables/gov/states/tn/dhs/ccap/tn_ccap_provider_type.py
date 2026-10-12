from policyengine_us.model_api import *


class TNCCAPProviderType(Enum):
    CHILD_CARE_CENTER = "Child care center"
    GROUP_HOME = "Group home"
    FAMILY_HOME = "Family home"
    AUTHORIZED = "Authorized"


class tn_ccap_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = TNCCAPProviderType
    default_value = TNCCAPProviderType.CHILD_CARE_CENTER
    definition_period = MONTH
    label = "Tennessee CCAP child care provider type"
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf"
