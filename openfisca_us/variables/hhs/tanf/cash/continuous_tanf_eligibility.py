from openfisca_us.model_api import *


class continuous_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Continued Economic Eligibility for TANF"
    documentation = "Whether the familiy meets the economic requirements for the Temporary Assistance for Needy Families program after being approved."
