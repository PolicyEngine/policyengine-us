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

    The deemors are the child's co-resident tax-unit members who are unlinked
    parents or a parent's spouse, and the spouse of each of those, wherever
    that spouse files (416.1202(b)(1): a parent and the parent's spouse).
    With no parent ids, is_parent cannot distinguish a grandparent or an
    unrelated parent from the child's parent: this is a data limitation.
    Keys hold every deemor's row, sorted, so children share a pool exactly
    when they share a deemor set.
    """
    parent = parent | ((spouse >= 0) & parent[np.maximum(spouse, 0)])
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
            selected = (member >= 0) & (households[safe] == households) & parent[safe]
            yield member, selected
            # Members of this tax unit are scanned above; add spouses who
            # file elsewhere. Each person has at most one spouse.
            partner = np.where(selected, spouse[safe], -1)
            outside = (partner >= 0) & (tax_units[np.maximum(partner, 0)] != tax_units)
            yield partner, outside

    count = np.zeros(person.count, dtype=int)
    for _, selected in deemors():
        count += selected
    keys = np.full((person.count, max(4, int(np.max(count, initial=0)))), -1)
    total = np.zeros(person.count)
    filled = np.zeros(person.count, dtype=int)
    for rows, selected in deemors():
        keys[indices[selected], filled[selected]] = rows[selected]
        total += np.where(selected, resources[np.maximum(rows, 0)], 0)
        filled += selected
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
        keys[linked] = -1
        keys[linked, :4] = named[linked]
    # Sorted rows make equal deemor sets equal keys, linked or not.
    keys.sort(axis=1)
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
        # SI 01330.200 B divides among SSI-eligible children. A child whose
        # countable income (with income deemed from parents) already reaches
        # the payment is ineligible 'for any reason': they are still deemed a
        # share, but do not count in the division. Neither variable reads the
        # resource test.
        income_eligible = person(
            "ssi_countable_income", period.this_year
        ) / MONTHS_IN_YEAR < person("ssi_amount_if_eligible", period)
        deemed = np.zeros(person.count)
        # SI 01330.200 B: 'equally divide' among eligible children; when a
        # child is ineligible 'divide ... among the remaining eligible children'.
        # A child outside the division is deemed the eligible children's share,
        # or the whole excess when none is left. Retain the last tested share
        # for a child who fails on resources, then redistribute.
        # Each round removes at least one child or leaves the result stable;
        # at most the largest household size rounds are needed (Goode, .280).
        rounds = int(np.max(person.household.nb_persons(), initial=0))
        pool_count = int(np.max(pool, initial=-1)) + 1
        for _ in range(rounds):
            count = np.bincount(pool[active & income_eligible], minlength=pool_count)
            share = excess / max_(1, count[pool])
            deemed = where(active, share, deemed)
            remaining = active & (own_resources + share <= p.individual)
            if np.array_equal(active, remaining):
                break
            active = remaining
        return deemed
