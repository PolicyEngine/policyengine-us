from policyengine_us.model_api import *


class roth_403b_contributions_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported Roth 403(b) contributions"
    unit = USD
    documentation = "Contributions reported to Roth 403(b) accounts before statutory contribution limits."
    definition_period = YEAR
