from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_known_claim_by_named_parent,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    tax_unit_parent_indices,
    unlinked_parent,
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
        # children even when parent-child links are not provided. A filer is
        # the presumed parent of a dependent without ids only when some of the
        # filer's children are named by no parent id; without links this is
        # is_parent.
        has_parent_filer_in_tax_unit = person.tax_unit.any(
            unlinked_parent(person, period)
            & person("is_tax_unit_head_or_spouse", period)
        )
        dependent = person("is_tax_unit_dependent", period)
        inferred_parent = (
            person("is_qualifying_child_dependent", period)
            | has_parent_filer_in_tax_unit
        )
        # A dependent's own ids name their parents. Parenthood does not depend
        # on residence, so resolve the ids among the members of the claiming
        # tax unit, wherever each lives, and require a parent to be the head
        # or spouse of that unit. The claiming unit is the dependent's own
        # unless a known claiming tax unit elsewhere claims them.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        first, second = tax_unit_parent_indices(person, period)
        linked_parent = ((first >= 0) & head_or_spouse[first]) | (
            (second >= 0) & head_or_spouse[second]
        )
        claimed_elsewhere, claimed_elsewhere_by_parent = (
            medicaid_known_claim_by_named_parent(person, period)
        )
        linked_parent = where(
            claimed_elsewhere, claimed_elsewhere_by_parent, linked_parent
        )
        return dependent & where(
            has_parent_ids(person, period), linked_parent, inferred_parent
        )
