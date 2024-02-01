from policyengine_us.model_api import *


class distributions_from_401k_accounts(Variable):
    value_type = float
    entity = Person
    label = "401k distributions"
    unit = USD
    documentation = "Distributions from 401k accounts."
    definition_period = YEAR
