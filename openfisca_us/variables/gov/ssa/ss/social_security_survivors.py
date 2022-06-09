from openfisca_us.model_api import *


class social_security_survivors(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors benefits"
    unit = USD
