from policyengine_us.model_api import *


class is_social_security_retirement(Variable):
    value_type = float
    entity = TaxUnit
    label = "Receive retirement benefits from employment exempt from Social Security"
    documentation = "Whether a recipient receive retirement benefits from employment exempt from Social Security"
    definition_period = YEAR
