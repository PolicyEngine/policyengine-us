from policyengine_us.model_api import *


class ak_was_atap_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was an Alaska Temporary Assistance Program (ATAP) recipient"
    definition_period = YEAR
    defined_for = StateCode.AK
    reference = "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-45-alaska-temporary-assistance-program"
