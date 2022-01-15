from openfisca_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Eligibility for Supplemental Security Income"
    label = "SSI eligibility"
