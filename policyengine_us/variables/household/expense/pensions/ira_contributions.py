from policyengine_us.model_api import *


class traditional_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA contributions"
    unit = USD
    documentation = (
        "Contributions to traditional Individual Retirement Accounts."
    )
    definition_period = YEAR
