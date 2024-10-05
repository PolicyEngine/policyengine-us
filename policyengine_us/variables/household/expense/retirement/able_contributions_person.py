from policyengine_us.model_api import *


class able_contributions_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level ABLE contributions"
    documentation = "Contributions made to an ABLE account by each individual."
    unit = USD
    definition_period = YEAR
