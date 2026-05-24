from policyengine_us.model_api import *


class roth_ira_contributions_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported Roth IRA contributions"
    unit = USD
    documentation = "Contributions reported to Roth Individual Retirement Accounts before statutory contribution limits."
    definition_period = YEAR
