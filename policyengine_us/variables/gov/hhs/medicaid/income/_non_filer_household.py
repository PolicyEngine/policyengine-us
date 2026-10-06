"""Medicaid MAGI household membership from parent links."""

import numpy as np

from policyengine_us.variables.gov.hhs.medicaid.income._medicaid_parents import (
    medicaid_parent_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    household_has_parent_ids,
    household_member_indices,
    unlinked_parent,
)


def _shares_parent_id(parent_1, parent_2, member):
    """Whether each person shares a nonzero parent id with a co-resident."""
    return (
        (parent_1 != 0)
        & ((parent_1 == parent_1[member]) | (parent_1 == parent_2[member]))
    ) | (
        (parent_2 != 0)
        & ((parent_2 == parent_1[member]) | (parent_2 == parent_2[member]))
    )


def _shares_co_resident_parent(first, second, member):
    """Whether each person shares a co-resident parent row with a co-resident."""
    return ((first >= 0) & ((first == first[member]) | (first == second[member]))) | (
        (second >= 0) & ((second == first[member]) | (second == second[member]))
    )


def _spouse_rule(person, period, first, second):
    """Return a test of whether a co-resident is each person's spouse.

    ``first`` and ``second`` are the co-resident parent rows
    (medicaid_parent_indices). A spouse is a
    co-resident partner in a two-person marital unit (PE's spouse
    convention), whatever either partner's tax role, or the other head or
    spouse of a joint return. A joint return or a cohabiting-spouses flag on
    either partner's tax unit shows the marriage. Otherwise the partners must
    share a family and no parent id, since PE puts everyone in one marital
    unit when a situation omits marital units. People linked as parent and
    child are never spouses.
    """
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    family = person.family.reference_entity.members_entity_id
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    head_spouse_count = person.tax_unit("head_spouse_count", period)
    joint = head_or_spouse & (head_spouse_count == 2)
    married = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id
    cohabiting = person.tax_unit("cohabitating_spouses", period)
    own_index = np.arange(person.count)

    def is_spouse(member):
        names_applicant = (first[member] == own_index) | (second[member] == own_index)
        named_by_applicant = (first == member) | (second == member)
        partner = married & (marital_unit[member] == marital_unit)
        return (
            (member != own_index)
            & ~names_applicant
            & ~named_by_applicant
            & (
                (joint & head_or_spouse[member] & (tax_unit[member] == tax_unit))
                | (partner & (cohabiting | cohabiting[member]))
                | (
                    partner
                    & (family[member] == family)
                    & ~_shares_parent_id(parent_1, parent_2, member)
                )
            )
        )

    return is_spouse


def medicaid_non_filer_member_sum(person, period, values):
    """Sum ``values`` once over each person's MAGI non-filer household.

    Callers use this in households with parent links and keep their original
    family-level expressions elsewhere. Under 42 CFR 435.603(f)(3) the
    household is the individual and, if living with the individual, (i) the
    spouse, (ii) the individual's children under the age limit and (iii) for
    an individual under the age limit, their parents and their siblings under
    the age limit. Each pair of co-residents is tested once, so each member
    counts once in size, income and California pregnancies.

    Links identify parents, children and siblings. Parents are
    medicaid_parent_indices: the co-resident parents the ids name, plus the
    established spouse of a lone named co-resident parent, since 42 CFR
    435.603(b) counts step relatives. Siblings share a nonzero parent id,
    including an absent parent's, or a co-resident parent, including an
    inferred step parent. A child-age person without ids is unlinked. The original family-level proxy still relates unlinked children
    to each other and to unlinked parents in their family (parents some of
    whose children no id names). So a parent that a child count reports is
    never erased, though moving a household onto this rule can remove another
    family's legacy over-count, such as an adult's child-age sibling.

    Spouses follow _spouse_rule.

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
    first, second = medicaid_parent_indices(person, period)
    family = person.family.reference_entity.members_entity_id

    def unlinked_parent_family(parent):
        # Family of a linked parent who is also an unlinked parent.
        return np.where((parent >= 0) & unlinked_parents[parent], family[parent], -1)

    parent_family_1 = unlinked_parent_family(first)
    parent_family_2 = unlinked_parent_family(second)

    is_spouse = _spouse_rule(person, period, first, second)

    own_index = np.arange(person.count)
    for member in household_member_indices(person):
        is_self = member == own_index
        same_family = family[member] == family
        names_applicant = (first[member] == own_index) | (second[member] == own_index)
        named_by_applicant = (first == member) | (second == member)
        shares_parent = _shares_parent_id(
            parent_1, parent_2, member
        ) | _shares_co_resident_parent(first, second, member)
        spouse = is_spouse(member)
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
                shares_parent
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


def medicaid_tax_dependent_spouse_sum(person, period, values):
    """Sum ``values`` over a tax dependent's spouse missing from their tax household.

    Callers add this to the tax-household branch in households with parent
    links and keep their original expressions elsewhere. Under 42 CFR
    435.603(f)(2) a tax dependent's household is the household of the
    taxpayer claiming them, and under (f)(4) each spouse of a married couple
    living together is in the other's household even when one is claimed as
    a dependent. The tax-household branch counts the members of the claiming
    tax unit, the people that unit claims from other units and a separately
    filing spouse of its head or spouse (the cohabiting-spouses flag, or
    medicaid_filer_spouse_sum), but never the dependent's own spouse. So for a
    tax dependent who uses that branch, this sums over the co-resident spouse
    _spouse_rule finds, unless the spouse already belongs to the tax
    household. It is zero for everyone else.

    Values accumulate in float64.
    """
    values = np.asarray(values, dtype=np.float64)
    total = np.zeros(person.count, dtype=np.float64)
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return total

    tax_unit = person.tax_unit.reference_entity.members_entity_id
    tax_unit_id = person.tax_unit("tax_unit_id", period)
    known_claim = person("medicaid_has_known_claiming_tax_unit", period)
    claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
    claimed_elsewhere = known_claim & (claiming_tax_unit_id != tax_unit_id)
    # The tax unit whose household the tax-household branch gives each person.
    household_tax_unit_id = np.where(known_claim, claiming_tax_unit_id, tax_unit_id)
    # A head or spouse whose tax household is their own unit's keeps that
    # unit's cohabiting-spouses channel for their own spouse.
    dependent = person("medicaid_is_tax_dependent", period) & (
        claimed_elsewhere | ~person("is_tax_unit_head_or_spouse", period)
    )
    applies = dependent & ~person("medicaid_uses_non_filer_rules", period)
    if not np.any(applies):
        return total

    first, second = medicaid_parent_indices(person, period)
    is_spouse = _spouse_rule(person, period, first, second)
    for member in household_member_indices(person):
        in_tax_household = np.where(
            known_claim,
            tax_unit_id[member] == claiming_tax_unit_id,
            tax_unit[member] == tax_unit,
        ) | (
            claimed_elsewhere[member]
            & (claiming_tax_unit_id[member] == household_tax_unit_id)
        )
        included = (member >= 0) & applies & is_spouse(member) & ~in_tax_household
        total += np.where(included, values[member], 0.0)
    return total


def medicaid_filer_spouse_sum(person, period, values):
    """Sum ``values`` over a head's or spouse's co-resident spouse outside their tax unit.

    Callers add each tax unit's total of this to every member's tax household,
    before claimants elsewhere look that household up. Under 42 CFR
    435.603(f)(1) a taxpayer's household is the taxpayer and the dependents
    they claim, (f)(4) adds a spouse the taxpayer lives with whether or not
    they file jointly, and under (f)(2) a dependent's household is the
    claiming taxpayer's. So, in households with parent links, a head or spouse
    counts the co-resident spouse _spouse_rule finds unless that spouse is
    already in the tax household: on the same return, or claimed into it from
    another unit. A unit whose cohabiting-spouses flag already adds its single
    head's separately filing spouse keeps that channel alone. It is zero for
    everyone else.

    Values accumulate in float64.
    """
    values = np.asarray(values, dtype=np.float64)
    total = np.zeros(person.count, dtype=np.float64)
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    if not np.any((parent_1 != 0) | (parent_2 != 0)):
        return total

    flagged = person.tax_unit("cohabitating_spouses", period) & (
        person.tax_unit("head_spouse_count", period) == 1
    )
    applies = (
        household_has_parent_ids(person, period)
        & person("is_tax_unit_head_or_spouse", period)
        & ~flagged
    )
    if not np.any(applies):
        return total

    tax_unit = person.tax_unit.reference_entity.members_entity_id
    tax_unit_id = person.tax_unit("tax_unit_id", period)
    claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
    claimed_elsewhere = person("medicaid_has_known_claiming_tax_unit", period) & (
        claiming_tax_unit_id != tax_unit_id
    )
    first, second = medicaid_parent_indices(person, period)
    is_spouse = _spouse_rule(person, period, first, second)
    for member in household_member_indices(person):
        in_tax_household = (tax_unit[member] == tax_unit) | (
            claimed_elsewhere[member] & (claiming_tax_unit_id[member] == tax_unit_id)
        )
        included = (member >= 0) & applies & is_spouse(member) & ~in_tax_household
        total += np.where(included, values[member], 0.0)
    return total
