from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_established_spouse_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    unlinked_parent,
)


def _ssi_unlinked_parental_resource_pool(person, resources, parent, spouse):
    """Return tax-unit/household proxy resources, count and exact pool keys.

    Only unlinked parents and their established spouses enter this proxy.
    With no parent ids, is_parent cannot distinguish a grandparent or an
    unrelated parent from the child's parent: this is a data limitation.
    The first four key columns hold deemor row indices. A proxy with more
    than four deemors cannot equal a linked pool (two parents and at most
    their two spouses), so its fifth column identifies its tax-unit and
    household intersection. Thus keys are exact, with linear memory.
    """
    named = parent
    parent = parent | ((spouse >= 0) & parent[spouse])
    group = person.tax_unit
    indices = np.arange(person.count)
    households = person.household.reference_entity.members_entity_id
    tax_units = group.reference_entity.members_entity_id
    total = np.zeros(person.count)
    count = np.zeros(person.count, dtype=int)
    keys = np.full((person.count, 5), -1, dtype=int)

    def add(rows, selected):
        nonlocal total, count
        store = selected & (count < 4)
        keys[indices[store], count[store]] = rows[store]
        total = total + np.where(selected, resources[np.maximum(rows, 0)], 0)
        count = count + selected

    for position in range(
        int(np.max(group.reference_entity.members_position, initial=-1)) + 1
    ):
        member = group.value_nth_person(position, indices, default=-1)
        safe = np.maximum(member, 0)
        selected = (member >= 0) & (households[safe] == households) & parent[safe]
        add(member, selected)
        # A parent's established spouse counts wherever they file
        # (416.1202(b)(1)); members of this tax unit were counted above.
        partner = np.where(selected & named[safe], spouse[safe], -1)
        add(partner, (partner >= 0) & (tax_units[np.maximum(partner, 0)] != tax_units))
    keys[:, :4].sort(axis=1)
    large = count > 4
    if np.any(large):
        _, intersections = np.unique(
            np.column_stack((group.reference_entity.members_entity_id, households)),
            axis=0,
            return_inverse=True,
        )
        keys[large, :4] = -1
        keys[large, 4] = intersections[large]
    return total, count, keys


def _ssi_parental_resource_pool(person, period, resources):
    """Resolve relationships first and identify children sharing deemors.

    416.1202(b)(1) includes named co-resident natural, adoptive or step
    parents, wherever their tax units, and an established co-resident spouse
    of each parent. Duplicate named/inferred parents count once. Without
    ids, use only unlinked_parent in the tax-unit proxy, as the parent-link
    contract requires. SI 01330.200 B divides the excess among children of
    the same parent(s), so allocation groups are exact deemor sets rather
    than tax units, including when linked and unlinked children share a set.
    """
    first, second = co_resident_parent_indices(person, period)
    spouse = _ssi_established_spouse_indices(person, period, first, second)
    total, count, keys = _ssi_unlinked_parental_resource_pool(
        person, resources, unlinked_parent(person, period), spouse
    )
    linked = has_parent_ids(person, period)
    if np.any(linked):
        first_spouse = np.where(first >= 0, spouse[first], -1)
        second_spouse = np.where(second >= 0, spouse[second], -1)
        named = np.column_stack((first, second, first_spouse, second_spouse))
        named.sort(axis=1)
        # Deduplicate before sorting again to give every identical set the
        # same key, independently of input parent slot or household order.
        named[:, 1:] = np.where(named[:, 1:] == named[:, :-1], -1, named[:, 1:])
        named.sort(axis=1)
        linked_total = np.sum(np.where(named >= 0, resources[named], 0), axis=1)
        linked_count = np.sum(named >= 0, axis=1)
        total = np.where(linked, linked_total, total)
        count = np.where(linked, linked_count, count)
        keys[linked, :4] = named[linked]
        keys[linked, 4] = -1
    _, pool = np.unique(keys, axis=0, return_inverse=True)
    return total, count, pool


class ssi_resources_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI resources deemed from ineligible parents"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1205",
        "https://www.ecfr.gov/current/title-20/section-416.1167",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330280",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330310",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330340",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        # Under 416.1167 a temporarily absent person should be entered in
        # the household they remain a member of; tax-unit membership alone
        # does not bring permanently nonresident relatives into that home.
        parental_resources, parent_count, pool = _ssi_parental_resource_pool(
            person, period, person("ssi_resources_for_deeming", period)
        )
        # 'only to the extent that those resources exceed the resource limits
        # described in § 416.1205': use the reformable individual/couple limits.
        allowance = where(parent_count > 1, p.couple, p.individual)
        excess = max_(0, parental_resources - allowance)
        # Do not discard ABD parents. SI 01330.310 B-C says zero if parent(s)
        # meets resource eligibility, usual deeming if not. The Ryder example
        # (.340) has an ABD mother failing the couple limit: 3100-3000=100.
        own_resources = person("ssi_countable_resources", period)
        active = person("is_ssi_resource_deeming_child", period) & (
            own_resources <= p.individual
        )
        deemed = np.zeros(person.count)
        # SI 01330.200 B: 'equally divide' among eligible children; when a
        # child is ineligible 'divide ... among the remaining eligible children'.
        # Retain the last tested share for a failed child, then redistribute.
        # Each round removes at least one child or leaves the result stable;
        # at most the largest household size rounds are needed (Goode, .280).
        rounds = int(np.max(person.household.nb_persons(), initial=0))
        pool_count = int(np.max(pool, initial=-1)) + 1
        for _ in range(rounds):
            count = np.bincount(pool[active], minlength=pool_count)
            share = excess / max_(1, count[pool])
            deemed = where(active, share, deemed)
            remaining = active & (own_resources + share <= p.individual)
            if np.array_equal(active, remaining):
                break
            active = remaining
        return deemed
