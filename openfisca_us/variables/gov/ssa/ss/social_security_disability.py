from openfisca_us.model_api import *


class social_security_disability(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security disability benefits (SSDI)"
    unit = USD
