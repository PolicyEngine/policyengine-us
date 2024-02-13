from policyengine_us.model_api import *


class traditional_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Traditional 401(k) contributions"
    unit = USD
    documentation = "Contributions to traditional 401(k) accounts."
    definition_period = YEAR
