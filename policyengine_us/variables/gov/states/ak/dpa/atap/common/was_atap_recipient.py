from policyengine_us.model_api import *


class was_atap_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was an Alaska Temporary Assistance Program (ATAP) recipient"
    definition_period = YEAR
    defined_for = StateCode.AK
    # 7 AAC 45 (Alaska Temporary Assistance Program regulations)
    reference = "https://www.akleg.gov/basis/aac.asp"
