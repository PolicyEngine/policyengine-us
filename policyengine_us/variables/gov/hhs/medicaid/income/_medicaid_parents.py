"""Medicaid MAGI parents: the ids' co-resident parents and one inferred step parent.

42 CFR 435.603(b) defines parents, children and siblings to include step
relatives. Ids often name a child's natural parents, one of whom lives
elsewhere, and leave out a step parent the child lives with. The inference here
is deliberately bounded:

- It applies only when the ids name exactly one distinct parent who lives with
  the person.
- The step parent is that parent's established co-resident spouse: the other
  head or spouse of a joint return, or the partner in a two-person marital unit
  whose tax unit (either partner's) carries the cohabiting-spouses flag. A
  two-person marital unit alone is not enough, since PE builds one marital unit
  for everyone when a situation omits marital units.
- Raw ids, including an absent parent's, are unchanged, so is_parent and
  sibling links through an absent parent's id are unaffected.

Larger parent graphs, such as a third co-resident parent or the step relatives
of a person whose ids name two co-resident parents, are not inferred.
"""

import numpy as np

from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    household_member_indices,
)


def medicaid_established_spouse_indices(person, period):
    """Row of each person's established co-resident spouse, or -1.

    A joint return or a two-person marital unit with the cohabiting-spouses
    flag on either partner's tax unit shows the marriage. Parent-child links
    rule out a candidate even when inferred tax roles suggest a marriage.
    A person with more than one such candidate has none.
    """
    first, second = co_resident_parent_indices(person, period)
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    joint = head_or_spouse & (person.tax_unit("head_spouse_count", period) == 2)
    married = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id
    cohabiting = person.tax_unit("cohabitating_spouses", period)
    own_index = np.arange(person.count)
    spouse = np.full(person.count, -1, dtype=int)
    candidates = np.zeros(person.count, dtype=int)
    for member in household_member_indices(person):
        # Tax roles can infer an adult child as the head's spouse. Raw
        # parent links rule out that marriage, as in _spouse_rule.
        names_applicant = (first[member] == own_index) | (second[member] == own_index)
        named_by_applicant = (first == member) | (second == member)
        shown = (
            (member >= 0)
            & (member != own_index)
            & ~names_applicant
            & ~named_by_applicant
            & (
                (joint & head_or_spouse[member] & (tax_unit[member] == tax_unit))
                | (
                    married
                    & (marital_unit[member] == marital_unit)
                    & (cohabiting | cohabiting[member])
                )
            )
        )
        spouse = np.where(shown, member, spouse)
        candidates += shown
    return np.where(candidates == 1, spouse, -1)


def medicaid_step_parent_index(person, period):
    """Row of each person's inferred co-resident step parent, or -1.

    When the ids name exactly one distinct parent the person lives with, this
    is that parent's established co-resident spouse, unless the spouse is the
    person or someone whose ids name the person as their parent.
    """
    first, second = co_resident_parent_indices(person, period)
    step = np.full(person.count, -1, dtype=int)
    one_parent = (first >= 0) != (second >= 0)
    if not np.any(one_parent):
        return step
    parent = np.where(first >= 0, first, second)
    spouse = medicaid_established_spouse_indices(person, period)
    step = np.where(one_parent, spouse[parent], -1)
    own_index = np.arange(person.count)
    names_person = (first[step] == own_index) | (second[step] == own_index)
    return np.where((step >= 0) & (step != own_index) & ~names_person, step, -1)


def medicaid_parent_indices(person, period):
    """Rows of each person's co-resident parents for Medicaid MAGI rules.

    The parents the ids name in the household, with an inferred step parent
    (medicaid_step_parent_index) in the empty slot. Unresolved slots are -1.
    """
    first, second = co_resident_parent_indices(person, period)
    step = medicaid_step_parent_index(person, period)
    fill_first = (first < 0) & (step >= 0)
    fill_second = (first >= 0) & (second < 0) & (step >= 0)
    return np.where(fill_first, step, first), np.where(fill_second, step, second)
