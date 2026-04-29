from policyengine_us.model_api import *


class SCCCAPQualityLevel(Enum):
    A_PLUS = "Level A+ (NAC)"
    A = "Level A (ERS)"
    B_PLUS = "Level B+ (EPC)"
    B = "Level B (ECR)"
    C = "Level C (LRC)"


class sc_ccap_quality_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = SCCCAPQualityLevel
    default_value = SCCCAPQualityLevel.C
    definition_period = MONTH
    label = "South Carolina CCAP provider quality level"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=1"
