from policyengine_us.model_api import *


class sd_ssp_care_died_or_transferred(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota SSP care recipient died or transferred to another long-term care facility this month"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06:09"
    documentation = "In a partial month, income is applied toward the cost of care only when the recipient died or transferred to another long-term care facility."
