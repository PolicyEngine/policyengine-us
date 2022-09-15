from openfisca_us.model_api import *


class is_child_of_tax_head(Variable):
    value_type = bool
    entity = Person
    label = "Is a child"
    definition_period = YEAR

    def formula(person, period, parameters):
        is_child_of_tax_head = person("is_child", period)
        return is_child_of_tax_head
