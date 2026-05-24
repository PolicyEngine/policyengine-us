from policyengine_us.model_api import *


class traditional_ira_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired traditional IRA contributions"
    unit = USD
    documentation = "Traditional IRA contributions before statutory contribution limits."
    definition_period = YEAR
