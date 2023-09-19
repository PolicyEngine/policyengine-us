from policyengine_us.model_api import *


class ira_distributions(Variable):
    value_type = float
    entity = Person
    label = "IRA distributions"
    unit = USD
    documentation = "Distributions from Individual Retirement Accounts."
    definition_period = YEAR
