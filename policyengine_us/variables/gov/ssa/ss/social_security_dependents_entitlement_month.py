from policyengine_us.model_api import *


class social_security_dependents_entitlement_month(Variable):
    value_type = int
    default_value = 1
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents entitlement month"
    documentation = "Recipient entitlement month (1 through 12)."
