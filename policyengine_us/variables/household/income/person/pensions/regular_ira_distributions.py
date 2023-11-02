from policyengine_us.model_api import *


class regular_ira_distributions(Variable):
    value_type = float
    entity = Person
    label = "Regular IRA distributions"
    unit = USD
    documentation = (
        "Distributions from regular individual retirement accounts."
    )
    definition_period = YEAR
