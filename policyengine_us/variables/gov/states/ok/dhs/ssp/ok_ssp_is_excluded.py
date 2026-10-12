from policyengine_us.model_api import *


class ok_ssp_is_excluded(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma SSP exclusion applies"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    documentation = "Public facility, psychiatric stay over 30 days, prohibited resource transfer, unmet benefit pursuit, or state-paid out-of-home child placement under 340:15-1-5(b)."
