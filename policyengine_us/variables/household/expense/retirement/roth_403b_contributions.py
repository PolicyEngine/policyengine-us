from policyengine_us.model_api import *


class roth_403b_contributions(Variable):
    value_type = float
    entity = Person
    label = "Roth 403(b) contributions"
    unit = USD
    documentation = "Contributions to Roth 403(b) accounts"
    definition_period = YEAR
