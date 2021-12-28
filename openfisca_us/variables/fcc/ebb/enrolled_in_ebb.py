from openfisca_us.model_api import *


class enrolled_in_ebb(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Enrolled for Emergency Broadband Benefit"
    documentation = "Whether a SPM unit is already enrolled in the Emergency Broadband Benefit"
    definition_period = YEAR
