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
        # Only non-head adults can be spouses, skipping input dependents.
        candidate = head_or_spouse_candidates(person, period)
        head = person("is_tax_unit_head", period)
        tax_unit = person.tax_unit
        age = person("age", period)
        spouse = person.get_rank(tax_unit, -age, candidate & ~head) == 0
        # Separation under 26 U.S.C. 7703 concerns the filer's own marriage, so
        # only the head's or this spouse's separation means there is no spouse.
        # A dependent's or other member's separation does not.
        separated = person("is_separated", period)
        head_or_spouse_separated = tax_unit.any((head | spouse) & separated)
        return spouse & ~head_or_spouse_separated
