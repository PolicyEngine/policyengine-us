from policyengine_us.model_api import *


class roth_ira_distributions(Variable):
    value_type = float
    entity = Person
    label = "Roth IRA distributions"
    unit = USD
    documentation = "Distributions from Roth individual retirement accounts."
    definition_period = YEAR
