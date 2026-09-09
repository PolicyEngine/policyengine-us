"""Household-scoped parent links, with linear temporary memory use."""

import numpy as np


def household_member_indices(person):
    """Yield each co-resident's row index, projected to every household member.

    Iterate over household positions, not pairs of people in the population.
    Membership comes from the entity structure, not optional household ID inputs.
    A missing position is -1 and must be masked before using its values.
    """
    indices = np.arange(person.count)
    positions = person.household.reference_entity.members_position
    for position in range(int(np.max(positions, initial=-1)) + 1):
        yield person.household.value_nth_person(position, indices, default=-1)


def co_resident_parent_indices(person, period):
    """Resolve the two parent slots to person rows; unknown links remain -1."""
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    first = np.full(person.count, -1, dtype=int)
    second = np.full(person.count, -1, dtype=int)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return first, second

    person_id = person("person_id", period)
    own_index = np.arange(person.count)
    for member in household_member_indices(person):
        valid = (member >= 0) & (member != own_index)
        member_id = person_id[member]
        first = np.where(
            valid & (parent_1 != 0) & (parent_1 == member_id), member, first
        )
        second = np.where(
            valid & (parent_2 != 0) & (parent_2 == member_id), member, second
        )
    return first, second


def parent_and_child_sibling_sum(person, period, child_age_eligible, values):
    """Sum applicant, co-resident parents, and child-age siblings once each.

    Used for the child non-filer household under 42 CFR 435.603(f)(3)(iv).
    Siblings share at least one nonzero parent ID, including half siblings.
    A shared absent parent can identify siblings without adding that parent.
    The caller selects its existing family sum when both parent IDs are zero.
    """
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    result = np.zeros(person.count, dtype=np.asarray(values).dtype)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return result

    person_id = person("person_id", period)
    own_index = np.arange(person.count)
    for member in household_member_indices(person):
        member_id = person_id[member]
        is_parent = ((parent_1 != 0) & (parent_1 == member_id)) | (
            (parent_2 != 0) & (parent_2 == member_id)
        )
        shares_parent = (
            (parent_1 != 0)
            & ((parent_1 == parent_1[member]) | (parent_1 == parent_2[member]))
        ) | (
            (parent_2 != 0)
            & ((parent_2 == parent_1[member]) | (parent_2 == parent_2[member]))
        )
        included = (member >= 0) & (
            (member == own_index)
            | is_parent
            | (child_age_eligible[member] & shares_parent)
        )
        result += np.where(included, values[member], 0)
    return result
