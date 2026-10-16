"""Co-resident parental resources shared by state supplement calculations."""

import numpy as np

from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    household_member_indices,
    unlinked_parent,
)


def ssp_parental_resources(person, period, parameters, exclude_ssi_parents=False):
    """Return the parent pair and resources above its SSI allowance.

    Explicit links identify natural, adoptive and step parents in this
    household. Without a child's links, use only explicitly identified
    unlinked parents in the same family and household. More than two such
    candidates requires parent links or a certified deemed-resource input.
    """
    year = period.this_year
    first, second = co_resident_parent_indices(person, year)
    unlinked = ~has_parent_ids(person, year)
    parent = unlinked_parent(person, year)
    family = person.family.reference_entity.members_entity_id
    own_row = np.arange(person.count)
    candidates = np.zeros(person.count, dtype=int)
    fallback_first = np.full(person.count, -1, dtype=int)
    fallback_second = np.full(person.count, -1, dtype=int)
    for member in household_member_indices(person):
        match = (
            (member >= 0)
            & (member != own_row)
            & parent[member]
            & (family[member] == family)
        )
        fallback_first = np.where(match & (candidates == 0), member, fallback_first)
        fallback_second = np.where(match & (candidates == 1), member, fallback_second)
        candidates = candidates + match
    usable = unlinked & (candidates <= 2)
    first = np.where(usable, fallback_first, first)
    second = np.where(usable, fallback_second, second)
    # Sorting makes sibling membership independent of the parent-slot order.
    first, second = np.minimum(first, second), np.maximum(first, second)
    resources = person("ssi_countable_resources", year).astype(np.float64)
    if exclude_ssi_parents:
        resources = np.where(person("ssi", period) > 0, 0, resources)
    total = np.where(first >= 0, resources[first], 0) + np.where(
        second >= 0, resources[second], 0
    )
    parents = (first >= 0).astype(int) + (second >= 0)
    limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit
    allowance = np.where(parents > 1, limit.couple, limit.individual)
    return first, second, np.maximum(total - allowance, 0)


def ssp_sibling_resource_share(person, first, second, excess, candidates, own, limit):
    """Allocate to otherwise eligible children, removing resource failures.

    SI 01330.200/.280 require reallocation when a child's own resources
    plus their share disqualify them. Children with different parent sets
    do not reduce one another's deemed resources.
    """
    eligible = candidates & (own <= limit)
    share = excess.copy()
    for _ in range(int(np.max(person.household.nb_persons(), initial=0)) + 1):
        count = np.zeros(person.count, dtype=int)
        for member in household_member_indices(person):
            same_parents = (first == first[member]) & (second == second[member])
            count = count + ((member >= 0) & same_parents & eligible[member])
        share = excess / np.maximum(count, 1)
        remaining = eligible & (own + share <= limit)
        if np.array_equal(remaining, eligible):
            break
        eligible = remaining
    return share
