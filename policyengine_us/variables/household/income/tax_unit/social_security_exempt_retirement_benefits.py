from policyengine_us.model_api import *


class social_security_exempt_retirement_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Retirement benefits amount from employment exempt from Social Security"
    documentation = "Amount of a recipient receive retirement benefits from employment exempt from Social Security"
    definition_period = YEAR
