from policyengine_us.model_api import *


class wic_food_package_str(Variable):
    value_type = str
    entity = Person
    label = "WIC food package (string)"
    documentation = "WIC food package variable, stored as a string"
    definition_period = MONTH

    def formula(person, period, parameters):
        return person("wic_food_package", period).decode_to_str()
