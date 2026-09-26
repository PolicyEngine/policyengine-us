"""Medicaid MAGI non-filer household membership from parent links."""

import numpy as np

from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    household_member_indices,
    reports_unlinked_children,
)


def medicaid_non_filer_member_sum(person, period, values):
    """Sum ``values`` once over each person's MAGI non-filer household.

    Callers use this in households with parent links and keep their original
    family-level expressions elsewhere. Under 42 CFR 435.603(f)(3) the
    household is the individual and, if living with the individual, (i) the
    spouse, (ii) the individual's children under the age limit and (iii) for
    an individual under the age limit, their parents and their siblings under
    the age limit. Each pair of co-residents is tested once, so each member
    counts once in size, income and California pregnancies.

    Links identify parents, children and siblings (siblings share a nonzero
    parent id, including an absent parent). A child-age person without ids is
    unlinked. The original family-level proxy still relates unlinked children
    to each other and to family members who report unlinked children, so one
    family's links never add or remove another family's relatives.

    A spouse is the other head or spouse of a joint return, or a cohabiting
    spouse under the separate-filer rule, and counts only when co-resident.

    Values accumulate in float64; variable storage rounds the result.
    """
    values = np.asarray(values, dtype=np.float64)
    total = np.zeros(person.count, dtype=np.float64)
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return total

    child = person("medicaid_non_filer_child_age_eligible", period)
    unlinked_child = child & ~has_parent_ids(person, period)
    reports_unlinked = reports_unlinked_children(person, period)
    first, second = co_resident_parent_indices(person, period)
    family = person.family.reference_entity.members_entity_id

    def reporting_parent_family(parent):
        # Family of a linked parent who also reports unlinked children.
        return np.where((parent >= 0) & reports_unlinked[parent], family[parent], -1)

    parent_family_1 = reporting_parent_family(first)
    parent_family_2 = reporting_parent_family(second)

    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    head_spouse_count = person.tax_unit("head_spouse_count", period)
    joint = head_or_spouse & (head_spouse_count == 2)
    separate_spouse = (
        person.tax_unit("cohabitating_spouses", period)
        & (head_spouse_count == 1)
        & (head_or_spouse | person("claimed_as_dependent_on_another_return", period))
    )
    marital_unit = person.marital_unit.reference_entity.members_entity_id

    own_index = np.arange(person.count)
    for member in household_member_indices(person):
        is_self = member == own_index
        same_family = family[member] == family
        spouse = ~is_self & (
            (joint & head_or_spouse[member] & (tax_unit[member] == tax_unit))
            | (separate_spouse & (marital_unit[member] == marital_unit))
        )
        own_child = child[member] & (
            (first[member] == own_index)
            | (second[member] == own_index)
            | (reports_unlinked & unlinked_child[member] & same_family)
        )
        parent = child & (
            (first == member)
            | (second == member)
            | (unlinked_child & reports_unlinked[member] & same_family)
        )
        shares_parent_id = (
            (parent_1 != 0)
            & ((parent_1 == parent_1[member]) | (parent_1 == parent_2[member]))
        ) | (
            (parent_2 != 0)
            & ((parent_2 == parent_1[member]) | (parent_2 == parent_2[member]))
        )
        sibling = (
            child
            & child[member]
            & ~is_self
            & (
                shares_parent_id
                | (
                    unlinked_child[member]
                    & (
                        (parent_family_1 == family[member])
                        | (parent_family_2 == family[member])
                    )
                )
                | (
                    unlinked_child
                    & (
                        (parent_family_1[member] == family)
                        | (parent_family_2[member] == family)
                    )
                )
                | (unlinked_child & unlinked_child[member] & same_family)
            )
        )
        included = (member >= 0) & (is_self | spouse | own_child | parent | sibling)
        total += np.where(included, values[member], 0.0)
    return total
