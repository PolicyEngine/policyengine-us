from policyengine_us.model_api import *


class traditional_403b_contributions(Variable):
    value_type = float
    entity = Person
    label = "Traditional 403(b) contributions"
    unit = USD
    documentation = "Contributions to traditional 403(b) accounts."
    definition_period = YEAR
