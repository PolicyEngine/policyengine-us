from policyengine_us.model_api import *


class was_atap_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was an Alaska Temporary Assistance Program (ATAP) recipient"
    definition_period = YEAR
    defined_for = StateCode.AK
    reference = "https://www.akleg.gov/basis/aac.asp#7.41.012"
