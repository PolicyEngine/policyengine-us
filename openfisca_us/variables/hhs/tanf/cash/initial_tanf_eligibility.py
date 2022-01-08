from openfisca_us.model_api import *


class initial_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Initial Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program on application."
