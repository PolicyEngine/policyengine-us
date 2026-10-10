from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


def _ssi_established_spouse_indices(person, period, first, second):
    """Rows of each person's co-resident spouse, or -1.

    SSI resource deeming uses this one test for a claimant's spouse
    (416.1202(a)), a parent's spouse (416.1202(b)) and whether a child is
    married (416.1856). A marital unit holds an unmarried person or a married,
    cohabiting couple, so the members of a two-person marital unit who live in
    the same household are spouses. So are the head and spouse of one tax
    unit who share a marital unit, which covers situations that omit marital
    units (those put everyone in one unit). Two people are never spouses when
    one claims the other as a tax dependent, since no one can claim a spouse,
    or when parent links name one as the other's parent; this keeps a default
    marital unit from pairing a parent with the child they claim. Ambiguous
    candidates resolve to no spouse.
    """
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    dependent = person("is_tax_unit_dependent", period)
    joint = head_or_spouse & person.tax_unit("tax_unit_married", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    couple = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id
    own_index = np.arange(person.count)
    spouse = np.full(person.count, -1, dtype=int)
    candidates = np.zeros(person.count, dtype=int)
    household = person.household
    for position in range(
        int(np.max(household.reference_entity.members_position, initial=-1)) + 1
    ):
        member = household.value_nth_person(position, own_index, default=-1)
        safe = np.maximum(member, 0)
        names_applicant = (first[safe] == own_index) | (second[safe] == own_index)
        named_by_applicant = (first == member) | (second == member)
        same_tax_unit = tax_unit[safe] == tax_unit
        # One claims the other when exactly one of them is a dependent of
        # the tax unit they share; two dependents can be a married couple.
        claims = same_tax_unit & (dependent != dependent[safe])
        same_marital_unit = marital_unit[safe] == marital_unit
        shown = (
            (member >= 0)
            & (member != own_index)
            & same_marital_unit
            & (couple | (joint & head_or_spouse[safe] & same_tax_unit))
            & ~claims
            & ~names_applicant
            & ~named_by_applicant
        )
        spouse = np.where(shown, member, spouse)
        candidates += shown
    return np.where(candidates == 1, spouse, -1)


def _ssi_spouse_index(person, period):
    """The row of each person's co-resident spouse, or -1."""
    first, second = co_resident_parent_indices(person, period)
    return _ssi_established_spouse_indices(person, period, first, second)
