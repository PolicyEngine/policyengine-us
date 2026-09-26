from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    household_has_parent_ids,
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
        qualifying_child = person("is_qualifying_child_dependent", period)
        # In tax-unit-only inputs, child dependents are usually the filer's
        # children even when parent-child links are not provided.
        has_parent_filer_in_tax_unit = person.tax_unit.any(
            person("is_parent", period) & head_or_spouse
        )
        inferred_parent = qualifying_child | has_parent_filer_in_tax_unit
        # In a household with parent links, a filer counts as the parent of a
        # dependent without ids only when the filer reports children the links
        # do not identify.
        has_unlinked_parent_filer_in_tax_unit = person.tax_unit.any(
            reports_unlinked_children(person, period) & head_or_spouse
        )
        residual_parent = qualifying_child | has_unlinked_parent_filer_in_tax_unit
        # A dependent's own ids name their parents. Parenthood does not depend
        # on residence, so resolve the ids among the dependent's tax unit
        # members, wherever each lives, and require a parent to be the head or
        # spouse of that unit.
        first, second = tax_unit_parent_indices(person, period)
        linked_parent = ((first >= 0) & head_or_spouse[first]) | (
            (second >= 0) & head_or_spouse[second]
        )
        return person("is_tax_unit_dependent", period) & where(
            has_parent_ids(person, period),
            linked_parent,
            where(
                household_has_parent_ids(person, period),
                residual_parent,
                inferred_parent,
            ),
        )
