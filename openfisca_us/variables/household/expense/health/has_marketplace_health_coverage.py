from openfisca_us.model_api import *


class has_marketplace_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Receives health insurance from a Marketplace plan."
    definition_period = YEAR
    default_value = True
