from policyengine_us.model_api import *


class roth_ira_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired Roth IRA contributions"
    unit = USD
    documentation = "Roth IRA contributions before statutory contribution limits."
    definition_period = YEAR
