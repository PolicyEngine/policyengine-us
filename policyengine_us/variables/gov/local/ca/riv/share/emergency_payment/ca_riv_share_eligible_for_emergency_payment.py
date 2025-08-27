from policyengine_us.model_api import *


class ca_riv_share_eligible_for_emergency_payment(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit has urgent notice and/or disconnection notice under Riverside County SHARE program"
    definition_period = MONTH
    defined_for = "in_riv"
    reference = "https://riversideca.gov/utilities/residents/assistance-programs/share-english"
