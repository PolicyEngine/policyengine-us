from policyengine_us.model_api import *


class co_social_security_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado social security subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = [
        "co_social_security_subtraction_head",
        "co_social_security_subtraction_spouse",
    ]
