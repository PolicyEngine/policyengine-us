from policyengine_us.model_api import *


class roth_401k_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired Roth 401(k) contributions"
    unit = USD
    documentation = "Roth 401(k) contributions before statutory contribution limits."
    definition_period = YEAR
