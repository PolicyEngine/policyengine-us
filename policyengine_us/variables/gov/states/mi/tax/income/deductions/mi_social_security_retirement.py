from policyengine_us.model_api import *


class mi_social_security_retirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Retirement benefits from employment exempt from Social Security"
    documentation = "Whether a recipient receive retirement benefits from employment exempt from Social Security"
    definition_period = YEAR
