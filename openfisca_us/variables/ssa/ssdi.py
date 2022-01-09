from openfisca_us.model_api import *


class ssdi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security Disability Insurance amount"
    label = "Social Security Disability Insurance"
    unit = USD
