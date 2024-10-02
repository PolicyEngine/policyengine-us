from policyengine_us.model_api import *


class able_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ABLE contributions"
    documentation = (
        "Contributions made to an ABLE account by all members of the tax unit."
    )
    unit = USD
    definition_period = YEAR

    adds = ["able_contributions_person"]
