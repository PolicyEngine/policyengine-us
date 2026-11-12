from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit._head_or_spouse_candidates import (
    head_or_spouse_candidates,
)


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
        # Otherwise only non-head adults can be spouses, skipping input
        # dependents.
        is_separated = tax_unit.any(person("is_separated", period))
        candidate = head_or_spouse_candidates(person, period)
        head = person("is_tax_unit_head", period)
        eligible = candidate & ~head & ~is_separated
        age = person("age", period)
        next_oldest_adult = person.get_rank(tax_unit, -age, eligible) == 0
        # An explicit is_tax_unit_head input still wins over a supplied role,
        # so keep the head out of the spouse role either way.
        supplied_spouse = (role == role.possible_values.SPOUSE) & ~head
        return where(supplied, supplied_spouse, next_oldest_adult)
