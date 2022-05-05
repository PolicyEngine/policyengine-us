from openfisca_us.model_api import *
from openfisca_core.populations import GroupPopulation, Population


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Only non-head adults can be spouses.
        adult = ~person("is_child", period)
        head = person("is_tax_unit_head", period)
        eligible = adult & ~head
        tax_unit = person.tax_unit
        age = person("age", period)
        return person.get_rank(tax_unit, -age, eligible) == 0
