from policyengine_us.model_api import *


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # A dataset's tax-unit constructor can supply every member's role.
        role = person("tax_unit_role_input", period)
        supplied = tax_unit("tax_unit_roles_supplied", period)
        # Otherwise only non-head adults can be spouses.
        is_separated = tax_unit.any(person("is_separated", period))
        adult = ~person("is_child", period)
        head = person("is_tax_unit_head", period)
        eligible = adult & ~head & ~is_separated
        age = person("age", period)
        next_oldest_adult = person.get_rank(tax_unit, -age, eligible) == 0
        return where(supplied, role == role.possible_values.SPOUSE, next_oldest_adult)
