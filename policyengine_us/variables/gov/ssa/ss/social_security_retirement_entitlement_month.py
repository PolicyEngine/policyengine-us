from policyengine_us.model_api import *


class social_security_retirement_entitlement_month(Variable):
    value_type = int
    default_value = 1
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement entitlement month"
    documentation = "Recipient entitlement month (1 through 12)."
