from openfisca_us.model_api import *


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Only adults can be heads.
        eligible = ~person("is_child", period)
        age = person("age", period)
        tax_unit = person.tax_unit
        return person.get_rank(tax_unit, -age, eligible) == 0
