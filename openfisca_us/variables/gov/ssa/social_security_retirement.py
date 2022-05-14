from openfisca_us.model_api import *


class social_security_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security retirement benefits"
    label = "Social Security retirement benefits"
    unit = USD
