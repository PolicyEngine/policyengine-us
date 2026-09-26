from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    reports_unlinked_children,
    tax_unit_parent_indices,
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
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # In tax-unit-only inputs, child dependents are usually the filer's
        # children even when parent-child links are not provided. A filer
        # counts as the parent of a dependent without ids only when the filer
        # reports own children that no parent id names; without links this is
        # own_children_in_household > 0, the original is_parent.
        has_parent_filer_in_tax_unit = person.tax_unit.any(
            reports_unlinked_children(person, period) & head_or_spouse
        )
        dependent = person("is_tax_unit_dependent", period)
        inferred_parent = (
            person("is_qualifying_child_dependent", period)
            | has_parent_filer_in_tax_unit
        )
        # A dependent's own ids name their parents. Parenthood does not depend
        # on residence, so resolve the ids among the dependent's tax unit
        # members, wherever each lives, and require a parent to be the head or
        # spouse of that unit.
        first, second = tax_unit_parent_indices(person, period)
        linked_parent = ((first >= 0) & head_or_spouse[first]) | (
            (second >= 0) & head_or_spouse[second]
        )
        return dependent & where(
            has_parent_ids(person, period), linked_parent, inferred_parent
        )
