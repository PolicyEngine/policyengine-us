from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


def _ssi_established_spouse_indices(person, period, first, second):
    """Rows of established co-resident spouses, with the Medicaid bound.

    SSI resource deeming uses this one test for a claimant's spouse
    (416.1202(a)) and for a parent's spouse (416.1202(b)). As in
    _medicaid_parents, marriage is shown by the other head/spouse of a
    married tax unit (here also in the same marital unit, so a tax-unit
    spouse role alone never makes a spouse of someone with their own marital
    unit), or by a two-person marital unit with cohabitating_spouses on
    either tax unit. A marital unit alone is insufficient: situations
    omitting marital units put everyone in one.
    Two dependents of one tax unit who share a two-person marital unit are
    spouses too, since a default marital unit also holds the tax unit's head
    and so never has two people. tax_unit_married is exactly when
    filing_status is JOINT; reading filing_status would pull the tax-filing
    chain (dependents, gross income, retirement-contribution limits) into SSI
    eligibility. Parent-child links exclude candidates even when tax roles
    suggest marriage; ambiguous candidates resolve to no spouse.
    """
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    joint = head_or_spouse & person.tax_unit("tax_unit_married", period)
    married = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id
    cohabiting = person.tax_unit("cohabitating_spouses", period)
    own_index = np.arange(person.count)
    spouse = np.full(person.count, -1, dtype=int)
    candidates = np.zeros(person.count, dtype=int)
    household = person.household
    for position in range(
        int(np.max(household.reference_entity.members_position, initial=-1)) + 1
    ):
        member = household.value_nth_person(position, own_index, default=-1)
        names_applicant = (first[member] == own_index) | (second[member] == own_index)
        named_by_applicant = (first == member) | (second == member)
        shown = (
            (member >= 0)
            & (member != own_index)
            & ~names_applicant
            & ~named_by_applicant
            & (
                (
                    joint
                    & head_or_spouse[member]
                    & (tax_unit[member] == tax_unit)
                    & (marital_unit[member] == marital_unit)
                )
                | (
                    married
                    & (marital_unit[member] == marital_unit)
                    & (
                        cohabiting
                        | cohabiting[member]
                        | (
                            ~head_or_spouse
                            & ~head_or_spouse[member]
                            & (tax_unit[member] == tax_unit)
                        )
                    )
                )
            )
        )
        spouse = np.where(shown, member, spouse)
        candidates += shown
    return np.where(candidates == 1, spouse, -1)


def _ssi_spouse_index(person, period):
    """The row of each person's established co-resident spouse, or -1."""
    first, second = co_resident_parent_indices(person, period)
    return _ssi_established_spouse_indices(person, period, first, second)
