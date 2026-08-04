from policyengine_us.model_api import *


class roth_403b_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired Roth 403(b) contributions"
    unit = USD
    documentation = "Roth 403(b) contributions before statutory contribution limits."
    definition_period = YEAR
