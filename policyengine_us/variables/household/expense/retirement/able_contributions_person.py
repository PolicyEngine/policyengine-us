from policyengine_us.model_api import *


class able_contributions_person(Variable):
    value_type = float
    entity = Person
    label = "ABLE contributions person"
    documentation = (
        "Contributions made to an ABLE account by each individiual person."
    )
    unit = USD
    definition_period = YEAR
