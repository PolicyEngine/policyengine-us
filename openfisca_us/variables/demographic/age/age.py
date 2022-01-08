from openfisca_us.model_api import *


class age(Variable):
    value_type = float
    entity = Person
    label = u"Age"
    definition_period = YEAR
    default_value = 18
