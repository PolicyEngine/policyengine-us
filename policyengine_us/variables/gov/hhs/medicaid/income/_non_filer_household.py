"""Medicaid MAGI non-filer household membership from parent links."""

import numpy as np

from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    household_member_indices,
    unlinked_parent,
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
    to each other and to unlinked parents in their family (parents some of
    whose children no id names). So a parent that a child count reports is
    never erased, though moving a household onto this rule can remove another
    family's legacy over-count, such as an adult's child-age sibling.

    A spouse is the other head or spouse of a joint return, or a co-resident
    partner in a two-person marital unit (PE's spouse convention) who is in
    the same family, whatever either partner's tax role. People linked as
    parent and child, or sharing a parent id, are never spouses. PE puts
    everyone in one marital unit, family and tax unit when a situation omits
    them, so supply those entities with parent ids.

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
    unlinked_parents = unlinked_parent(person, period)
    first, second = co_resident_parent_indices(person, period)
    family = person.family.reference_entity.members_entity_id

    def unlinked_parent_family(parent):
        # Family of a linked parent who is also an unlinked parent.
        return np.where((parent >= 0) & unlinked_parents[parent], family[parent], -1)

    parent_family_1 = unlinked_parent_family(first)
    parent_family_2 = unlinked_parent_family(second)

    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    head_spouse_count = person.tax_unit("head_spouse_count", period)
    joint = head_or_spouse & (head_spouse_count == 2)
    married = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id

    own_index = np.arange(person.count)
    for member in household_member_indices(person):
        is_self = member == own_index
        same_family = family[member] == family
        names_applicant = (first[member] == own_index) | (second[member] == own_index)
        named_by_applicant = (first == member) | (second == member)
        shares_parent_id = (
            (parent_1 != 0)
            & ((parent_1 == parent_1[member]) | (parent_1 == parent_2[member]))
        ) | (
            (parent_2 != 0)
            & ((parent_2 == parent_1[member]) | (parent_2 == parent_2[member]))
        )
        spouse = (
            ~is_self
            & ~names_applicant
            & ~named_by_applicant
            & ~shares_parent_id
            & (
                (joint & head_or_spouse[member] & (tax_unit[member] == tax_unit))
                | (married & (marital_unit[member] == marital_unit) & same_family)
            )
        )
        own_child = child[member] & (
            names_applicant | (unlinked_parents & unlinked_child[member] & same_family)
        )
        parent = child & (
            named_by_applicant
            | (unlinked_child & unlinked_parents[member] & same_family)
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
