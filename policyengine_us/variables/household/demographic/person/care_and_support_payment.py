from policyengine_us.model_api import *


class care_and_support_payment(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = (
        "Amount of payments made for care and support of this person"
    )
