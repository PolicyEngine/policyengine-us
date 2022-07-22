from openfisca_us.model_api import *


class wic_category_str(Variable):
    value_type = str
    entity = Person
    label = "WIC category (string)"
    documentation = "WIC category variable, stored as a string"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("wic_category", period).decode_to_str()
