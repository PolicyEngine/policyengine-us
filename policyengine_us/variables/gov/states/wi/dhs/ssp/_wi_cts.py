from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    household_has_parent_ids,
)


def cts_ssi_recipient(person, period):
    return (person("ssi", period) > 0) | person("receives_ssi", period)


def cts_relationships(person, period):
    first, second = co_resident_parent_indices(person, period.this_year)
    linked = household_has_parent_ids(person, period.this_year)
    # Handbook 3.1.3: a CTS parent receives the Wisconsin state SSI payment.
    # Grandfathered state-only SSI recipients are not modeled.
    receipt = person("wi_ssp_regular", period) > 0
    parents = (first >= 0).astype(int) + (second >= 0)
    ssi_parents = ((first >= 0) & receipt[first]).astype(int) + (
        (second >= 0) & receipt[second]
    )
    is_parent = person("is_parent", period.this_year)
    parents = where(linked, parents, person.family.sum(is_parent))
    ssi_parents = where(linked, ssi_parents, person.family.sum(is_parent & receipt))
    return first, second, linked, receipt, parents, ssi_parents


def cts_unit_sum(unit, values):
    """Total of values over each person's filing unit; 0 outside any unit."""
    in_unit = unit >= 0
    totals = np.bincount(
        unit[in_unit],
        weights=np.asarray(values, dtype=float)[in_unit],
        minlength=unit.size,
    )
    return where(in_unit, totals[max_(unit, 0)], 0)


def _lowest_child_unit(unit, first, second, child, count):
    """Lowest unit key among each parent's co-resident children (count if none)."""
    lowest = np.full(count, count)
    for parent in (first, second):
        rows = child & (parent >= 0)
        np.minimum.at(lowest, parent[rows], unit[rows])
    return lowest


def cts_filing_unit(person, period):
    """Each person's standard filing unit key (-1 if none), members and Buening subgroup.

    Handbook 3.1.1 and 3.2.1.2.1 (#page=18, #page=30): non-SSI dependent
    children who share a co-resident parent belong to one unit with their
    parents, so a unit holds a target child's full and half siblings and
    their parents; half-sibling links are followed transitively. An SSI
    child does not link its siblings (5.4.1 Scenarios 7 and 8, #page=71). A
    unit forms only around a child with an SSI parent. Without parent links
    each family is one unit.
    """
    first, second, linked, _, _, ssi_parents = cts_relationships(person, period)
    count = person.count
    index = np.arange(count)
    on_ssi = cts_ssi_recipient(person, period)
    child = person("wi_cts_dependent_child", period) & ~on_ssi
    # Give every child the lowest key reachable through shared parents.
    unit = where(child, index, count)
    while True:
        parent_unit = _lowest_child_unit(unit, first, second, child, count)
        joined = unit
        for parent in (first, second):
            joined = where(
                child & (parent >= 0), min_(joined, parent_unit[parent]), joined
            )
        if np.array_equal(joined, unit):
            break
        unit = joined
    parent = parent_unit < count
    unit = where(child, unit, where(parent, parent_unit, -1))
    unit = where(linked, unit, person.family.min(index)).astype(int)
    target = child & (ssi_parents > 0)
    unit = where(cts_unit_sum(unit, target) > 0, unit, -1)
    parent = where(linked, parent, person("is_parent", period.this_year))
    member = (child | parent) & ~on_ssi & (unit >= 0)
    # Handbook 3.3.1 (#page=33): the non-SSI co-parent and the children
    # related to them are tested separately under Buening.
    co_parent = linked & member & ~child
    related = ((first >= 0) & co_parent[first]) | ((second >= 0) & co_parent[second])
    return unit, member, member & (co_parent | related)


def cts_financial_test(person, period, parameters, unit, group, large_group_limit):
    """Whether each person's unit group passes the income and asset tests.

    Also returns whether the group's net income limit is known: the
    published tables end at one size, and a larger group needs a verified
    limit (large_group_limit, 0 when none).
    """
    p = parameters(period).gov.states.wi.dhs.ssp.cts
    size = cts_unit_sum(unit, group)
    pregnant = cts_unit_sum(unit, group & person("is_pregnant", period.this_year))
    area_i = person("wi_cts_area_i", period)
    gross_limit = where(area_i, p.gross.area_1.calc(size), p.gross.area_2.calc(size))
    pregnancy_gross_limit = where(
        area_i,
        p.gross_pregnant.area_1.calc(size),
        p.gross_pregnant.area_2.calc(size),
    )
    # The pregnancy table includes one allowance; each further pregnant
    # woman adds another (Handbook 5.2.2).
    gross_limit = where(
        pregnant > 0,
        pregnancy_gross_limit + max_(pregnant - 1, 0) * p.pregnancy_allowance,
        gross_limit,
    )
    # The gross, pregnancy and net tables all end at the same group size.
    table_size = p.net.area_1.thresholds[-1]
    gross_limit = gross_limit + max_(size - table_size, 0) * p.gross_additional
    published = size <= table_size
    net_limit = where(
        published,
        where(area_i, p.net.area_1.calc(size), p.net.area_2.calc(size))
        + pregnant * p.pregnancy_allowance,
        large_group_limit,
    )
    gross = cts_unit_sum(unit, group * person("wi_cts_gross_income", period))
    net = cts_unit_sum(
        unit,
        group
        * (
            person("wi_cts_net_income", period)
            - person("wi_cts_dependent_care_deduction", period)
            - max_(person("child_support_expense", period), 0)
        ),
    )
    assets = cts_unit_sum(
        unit, group * max_(person("wi_cts_countable_resources", period), 0)
    )
    eligible = (
        (gross <= gross_limit)
        & (max_(net, 0) <= net_limit)
        & (assets <= p.resource_limit)
    )
    return eligible, published | (large_group_limit > 0)
