"""Parent links from the optional parent_1_id and parent_2_id person inputs.

Rules shared by every formula that reads the links:

- Each id names the person_id of one of the person's parents (natural,
  adoptive or step); 0 means unknown, so real person ids must be nonzero.
- Parenthood is identity and residence is a separate condition. Ids resolve
  against the members of one group entity: the household when a rule requires
  living together, the tax unit when a rule asks who claims the person.
- A person is a parent when own_children_in_household is positive or when a
  co-resident person's id names them. Neither source erases the other.
- A household has links when any member has a nonzero id. Formulas keep
  their original expressions in households without links.
- In a household with links, a person reports unlinked children when
  own_children_in_household exceeds the co-resident people whose ids name
  them. Such a person is the only kind of parent the family-level proxy may
  still assign to a child-age member without ids.

Temporary memory is linear in the number of people, and work is linear in
people times the largest household or tax unit size.
"""

import numpy as np


def group_member_indices(group):
    """Yield each co-member's row index, projected to every member of a group.

    ``group`` is a person-level projector such as ``person.household``.
    Iterate over positions within the group, not over pairs of people.
    Membership comes from the entity structure, not optional group ID inputs.
    A missing position is -1 and must be masked before using its values.
    """
    indices = np.arange(group.reference_entity.members.count)
    positions = group.reference_entity.members_position
    for position in range(int(np.max(positions, initial=-1)) + 1):
        yield group.value_nth_person(position, indices, default=-1)


def household_member_indices(person):
    """Yield each co-resident's row index, projected to every household member."""
    return group_member_indices(person.household)


def has_parent_ids(person, period):
    return (person("parent_1_id", period) != 0) | (person("parent_2_id", period) != 0)


def household_has_parent_ids(person, period):
    """Whether any member of each person's household has a nonzero parent id."""
    return person.household.any(has_parent_ids(person, period))


def _parent_indices(person, period, group):
    """Resolve both parent slots among the members of ``group``.

    Unresolved slots are -1. A second slot that repeats the first names no
    second parent, so each resolved parent appears once per person.
    """
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    first = np.full(person.count, -1, dtype=int)
    second = np.full(person.count, -1, dtype=int)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return first, second

    person_id = person("person_id", period)
    own_index = np.arange(person.count)
    for member in group_member_indices(group):
        valid = (member >= 0) & (member != own_index)
        member_id = person_id[member]
        first = np.where(
            valid & (parent_1 != 0) & (parent_1 == member_id), member, first
        )
        second = np.where(
            valid & (parent_2 != 0) & (parent_2 == member_id), member, second
        )
    second = np.where(second == first, -1, second)
    return first, second


def co_resident_parent_indices(person, period):
    """Rows of the parents each person's ids name within their household."""
    return _parent_indices(person, period, person.household)


def tax_unit_parent_indices(person, period):
    """Rows of the parents each person's ids name within their tax unit.

    A parent who claims the person is recognized wherever either one lives.
    """
    return _parent_indices(person, period, person.tax_unit)


def linked_child_count(person, period):
    """Count the co-resident people whose parent ids name each person."""
    first, second = co_resident_parent_indices(person, period)
    parents = np.concatenate((first, second))
    return np.bincount(parents[parents >= 0], minlength=person.count)


def reports_unlinked_children(person, period):
    """Whether a person reports more own children than the links identify.

    In a household without links this equals own_children_in_household > 0.
    """
    return person("own_children_in_household", period) > linked_child_count(
        person, period
    )
