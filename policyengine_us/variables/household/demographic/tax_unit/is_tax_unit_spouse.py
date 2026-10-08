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
        is_separated = person.tax_unit.any(person("is_separated", period))
        candidate = head_or_spouse_candidates(person, period)
        head = person("is_tax_unit_head", period)
        eligible = candidate & ~head & ~is_separated
        tax_unit = person.tax_unit
        age = person("age", period)
        return person.get_rank(tax_unit, -age, eligible) == 0
