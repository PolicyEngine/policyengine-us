from policyengine_us.model_api import *


class roth_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Roth IRA contributions"
    unit = USD
    documentation = "Contributions to Roth Individual Retirement Accounts."
    definition_period = YEAR
