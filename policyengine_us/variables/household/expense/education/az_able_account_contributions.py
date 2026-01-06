from policyengine_us.model_api import *


class az_able_account_contributions(Variable):
    value_type = float
    entity = Person
    label = "Arizona ABLE account contributions"
    unit = USD
    documentation = (
        "Amount contributed to a 529A ABLE account for disabled beneficiaries."
    )
    definition_period = YEAR
