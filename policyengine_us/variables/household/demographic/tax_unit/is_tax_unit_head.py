from policyengine_us.model_api import *


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # A dataset's tax-unit constructor can supply every member's role.
        role = person("tax_unit_role_input", period)
        supplied = tax_unit("tax_unit_roles_supplied", period)
        # Otherwise only adults can be heads, and the oldest is the head.
        eligible = ~person("is_child", period)
        age = person("age", period)
        oldest_adult = person.get_rank(tax_unit, -age, eligible) == 0
        return where(supplied, role == role.possible_values.HEAD, oldest_adult)
