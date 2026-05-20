from policyengine_us.model_api import *


class SCCCAPRegisteredQualityLevel(Enum):
    B_PLUS = "Level B+ (EPC)"
    B = "Level B (ECR)"
    C = "Level C (LRC)"


class sc_ccap_registered_quality_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = SCCCAPRegisteredQualityLevel
    default_value = SCCCAPRegisteredQualityLevel.C
    definition_period = MONTH
    label = "South Carolina CCAP registered family home quality level"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=11"
