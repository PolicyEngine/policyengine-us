from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_established_spouse_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    unlinked_parent,
)


def _ssi_unlinked_parental_deemors(person, period, spouse, with_spouses):
    """Return tax-unit/household proxy deemor rows and their count.

    The deemors are the person's co-resident tax-unit members who are unlinked
    parents or a parent's spouse, and the spouse of each of those, wherever
    that spouse files (416.1160(d), 416.1202(b)(1): a parent and the parent's
    spouse). Without with_spouses only the unlinked parents count. With no
    parent ids, is_parent cannot distinguish a grandparent or an unrelated
    parent from the child's parent: this is a data limitation. A person who
    is an unlinked parent is in their own set, as in the proxy sets of the
    siblings they share a tax unit with, so a teen parent and their brothers
    and sisters keep one pool. Income deeming never counts the person as
    their own ineligible parent.
    """
    unlinked = unlinked_parent(person, period)
    has_spouse = spouse >= 0
    parent_or_spouse = unlinked | (has_spouse & unlinked[np.maximum(spouse, 0)])
    group = person.tax_unit
    indices = np.arange(person.count)
    households = person.household.reference_entity.members_entity_id
    tax_units = group.reference_entity.members_entity_id
    positions = range(
        int(np.max(group.reference_entity.members_position, initial=-1)) + 1
    )

    def deemors():
        for position in positions:
            member = group.value_nth_person(position, indices, default=-1)
            safe = np.maximum(member, 0)
            selected = (
                (member >= 0)
                & (households[safe] == households)
                & where(with_spouses, parent_or_spouse[safe], unlinked[safe])
            )
            yield member, selected
            # Members of this tax unit are scanned above; add spouses who
            # file elsewhere. Each person has at most one spouse.
            partner = np.where(selected & with_spouses, spouse[safe], -1)
            outside = (partner >= 0) & (tax_units[np.maximum(partner, 0)] != tax_units)
            yield partner, outside

    count = np.zeros(person.count, dtype=int)
    for _, selected in deemors():
        count += selected
    rows = np.full((person.count, max(4, int(np.max(count, initial=0)))), -1)
    filled = np.zeros(person.count, dtype=int)
    for members, selected in deemors():
        rows[indices[selected], filled[selected]] = members[selected]
        filled += selected
    return rows


def ssi_parental_deemors(person, period, with_spouses=True):
    """Return each person's parental deemor rows and a pool id per set.

    20 CFR 416.1160(d): an ineligible parent is 'a natural or adoptive
    parent, or the spouse ... of a natural or adoptive parent, who lives with
    you'; 416.1202(b)(1) names the same people for resources. A person's
    deemors are their named co-resident natural, adoptive or step parents,
    wherever those file, and an established co-resident spouse of each.
    Duplicate named or inferred parents count once. Without ids, only
    unlinked parents enter the tax-unit proxy, as the parent-link contract
    requires. SSI eligibility is not tested here: income deeming drops
    eligible parents (416.1165(g)(1)), resource deeming keeps them (POMS SI
    01330.310). with_spouses (a bool or a per-person array) set to False
    keeps the named or presumed parents only, without their spouses.

    Returns rows, an int array with one row per person holding their deemors'
    row indices sorted ascending and padded with -1 (first), and pool, an int
    array equal for people whose deemor sets are equal. SI 01330.200 B and
    416.1165(e)(2) divide among the children of the same parent(s), so these
    pools are exact deemor sets rather than tax units, including when linked
    and unlinked children share a set.
    """
    with_spouses = np.broadcast_to(with_spouses, (person.count,))
    first, second = co_resident_parent_indices(person, period)
    spouse = _ssi_established_spouse_indices(person, period, first, second)
    rows = _ssi_unlinked_parental_deemors(person, period, spouse, with_spouses)
    linked = has_parent_ids(person, period)
    if np.any(linked):
        first_spouse = np.where((first >= 0) & with_spouses, spouse[first], -1)
        second_spouse = np.where((second >= 0) & with_spouses, spouse[second], -1)
        named = np.column_stack((first, second, first_spouse, second_spouse))
        named.sort(axis=1)
        # Deduplicate before sorting again to give every identical set the
        # same key, independently of input parent slot or household order.
        named[:, 1:] = np.where(named[:, 1:] == named[:, :-1], -1, named[:, 1:])
        named.sort(axis=1)
        rows[linked] = -1
        rows[linked, :4] = named[linked]
    # Sorted rows make equal deemor sets equal keys, linked or not.
    rows.sort(axis=1)
    _, pool = np.unique(rows, axis=0, return_inverse=True)
    return rows, pool.reshape(-1)
