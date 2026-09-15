from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


class medicaid_claimed_by_parent_in_tax_unit(Variable):
    value_type = bool
    entity = Person
    label = (
        "Claimed by a parent in the current tax unit for Medicaid MAGI household rules"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"

    def formula(person, period, parameters):
        # In tax-unit-only inputs, child dependents are usually the filer's
        # children even when parent-child links are not provided.
        has_parent_filer_in_tax_unit = person.tax_unit.any(
            person("is_parent", period) & person("is_tax_unit_head_or_spouse", period)
        )
        inferred_parent = (
            person("is_qualifying_child_dependent", period)
            | has_parent_filer_in_tax_unit
        )
        first, second = co_resident_parent_indices(person, period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        linked_parent = (
            (first >= 0) & head_or_spouse[first] & (tax_unit[first] == tax_unit)
        ) | ((second >= 0) & head_or_spouse[second] & (tax_unit[second] == tax_unit))
        has_parent_ids = (person("parent_1_id", period) != 0) | (
            person("parent_2_id", period) != 0
        )
        return person("is_tax_unit_dependent", period) & where(
            has_parent_ids, linked_parent, inferred_parent
        )
