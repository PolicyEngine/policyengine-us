from policyengine_us.model_api import *


class oh_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is already enrolled in Ohio CCAP"
    defined_for = StateCode.OH
    reference = "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=2"
