from policyengine_us.model_api import *


class roth_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Roth 401(k) contributions"
    unit = USD
    documentation = "Contributions to Roth 401(k) accounts."
    definition_period = YEAR
