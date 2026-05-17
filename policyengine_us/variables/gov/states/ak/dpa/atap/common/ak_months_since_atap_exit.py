from policyengine_us.model_api import *


class ak_months_since_atap_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since Alaska Temporary Assistance Program (ATAP) case closed"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-45-alaska-temporary-assistance-program"
