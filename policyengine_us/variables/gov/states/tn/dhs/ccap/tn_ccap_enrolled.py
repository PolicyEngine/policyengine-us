from policyengine_us.model_api import *


class tn_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is already enrolled in Tennessee CCAP"
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Income%20Eligibility%20Limits%20and%20CoPay%20Chart%2010.1.25.pdf#page=1"
