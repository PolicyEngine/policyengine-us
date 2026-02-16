from policyengine_us.model_api import *


class would_claim_wic(Variable):
    value_type = bool
    entity = Person
    label = "Would claim WIC"
    definition_period = MONTH
    default_value = True
