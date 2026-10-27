from policyengine_us.model_api import *


class social_security_disability_entitlement_year(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security disability entitlement year"
    documentation = "Recipient entitlement year; zero means unavailable."
