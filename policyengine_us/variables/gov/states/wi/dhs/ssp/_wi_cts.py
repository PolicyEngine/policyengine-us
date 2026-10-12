import numpy as np
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    household_has_parent_ids,
)


def cts_relationships(person, period):
    first, second = co_resident_parent_indices(person, period.this_year)
    linked = household_has_parent_ids(person, period.this_year)
    receipt = (person("wi_ssp_regular", period) > 0) | person(
        "wi_cts_state_only_ssi_recipient", period
    )
    parents = (first >= 0).astype(int) + (second >= 0)
    ssi_parents = ((first >= 0) & receipt[first]).astype(int) + (
        (second >= 0) & receipt[second]
    )
    is_parent = person("is_parent", period.this_year)
    parents = np.where(linked, parents, person.family.sum(is_parent))
    ssi_parents = np.where(linked, ssi_parents, person.family.sum(is_parent & receipt))
    return first, second, linked, receipt, parents, ssi_parents


def cts_filing_unit(person, period):
    first, second, linked, receipt, parents, ssi_parents = cts_relationships(
        person, period
    )
    child = person("wi_cts_dependent_child", period)
    on_ssi = (person("ssi", period) > 0) | receipt
    candidate = child & ~on_ssi & (ssi_parents > 0)
    common = candidate & (parents > 1)
    candidate = np.where(person.family.any(common), common, candidate)
    age = person("age", period.this_year)
    oldest = person.family.max(np.where(candidate, age, -1))
    target = candidate & (age == oldest)
    # Selecting both tied oldest siblings is harmless: their union determines
    # the same filing unit for ordinary twin/sibling configurations.
    target_first = person.family.max(np.where(target, first, -1))
    target_second = person.family.max(np.where(target, second, -1))
    siblings = child & (
        ((first >= 0) & ((first == target_first) | (first == target_second)))
        | ((second >= 0) & ((second == target_first) | (second == target_second)))
    )
    parent_rows = np.concatenate((first[siblings], second[siblings]))
    parent_mask = np.bincount(parent_rows[parent_rows >= 0], minlength=person.count) > 0
    member = (siblings | parent_mask) & ~on_ssi
    fallback = (child | person("is_parent", period.this_year)) & ~on_ssi
    member = np.where(linked, member, fallback)
    non_ssi_parent = parent_mask & ~on_ssi
    related_to_non_ssi = ((first >= 0) & non_ssi_parent[first]) | (
        (second >= 0) & non_ssi_parent[second]
    )
    subgroup = member & (non_ssi_parent | related_to_non_ssi)
    return member, np.where(linked, subgroup, False)


def cts_income_limits(person, period, parameters, members, buening=False):
    p = parameters(period).gov.states.wi.dhs.ssp.cts
    size = person.family.sum(members)
    area_i = person("wi_cts_area_i", period)
    pregnant = person.family.sum(members & person("is_pregnant", period.this_year))
    gross = np.where(area_i, p.gross.area_1.calc(size), p.gross.area_2.calc(size))
    pregnancy_gross = np.where(
        area_i, p.gross_pregnant.area_1.calc(size), p.gross_pregnant.area_2.calc(size)
    )
    gross = np.where(
        pregnant > 0,
        pregnancy_gross + np.maximum(pregnant - 1, 0) * p.pregnancy_net,
        gross,
    )
    gross = gross + np.maximum(size - p.maximum_table_size, 0) * p.gross_additional
    net = (
        np.where(area_i, p.net.area_1.calc(size), p.net.area_2.calc(size))
        + pregnant * p.pregnancy_net
    )
    limit_name = (
        "wi_cts_buening_large_group_net_income_limit"
        if buening
        else "wi_cts_large_group_net_income_limit"
    )
    verified_limit = person.family(limit_name, period)
    table_covers_group = size <= p.maximum_table_size
    net = np.where(table_covers_group, net, verified_limit)
    known = table_covers_group | (verified_limit > 0)
    return gross, net, known
