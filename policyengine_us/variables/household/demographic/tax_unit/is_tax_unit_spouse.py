from policyengine_us.model_api import *


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Only non-head adults can be spouses.
        is_separated = person.tax_unit.any(person("is_separated", period))
        adult = ~person("is_child", period)
        head = person("is_tax_unit_head", period)
        eligible = adult & ~head & ~is_separated
        tax_unit = person.tax_unit
        age = person("age", period)
        return person.get_rank(tax_unit, -age, eligible) == 0
