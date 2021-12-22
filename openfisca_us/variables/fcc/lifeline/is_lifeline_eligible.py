from openfisca_us.model_api import *


class is_lifeline_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Lifeline"
    description = "Eligible for Lifeline phone or broadband subsidy"
    definition_period = YEAR
