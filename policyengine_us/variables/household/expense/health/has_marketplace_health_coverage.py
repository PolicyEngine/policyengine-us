from policyengine_us.model_api import *


class has_marketplace_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Is eligible for health insurance from an ACA Marketplace plan because has no employer-sponsored health insurance coverage."
    definition_period = YEAR
    default_value = True
