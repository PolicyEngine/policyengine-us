from policyengine_us.model_api import *


class is_sd_cca_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Enrolled in South Dakota CCA"
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=21"
    )
