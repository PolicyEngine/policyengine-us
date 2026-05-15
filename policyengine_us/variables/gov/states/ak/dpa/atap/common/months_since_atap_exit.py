from policyengine_us.model_api import *


class months_since_atap_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since Alaska Temporary Assistance Program (ATAP) case closed"
    definition_period = MONTH
    defined_for = StateCode.AK
    # 7 AAC 45 (Alaska Temporary Assistance Program regulations)
    reference = "https://www.akleg.gov/basis/aac.asp"
