"""Relationship scope for allocations deducted before parental income deeming."""

import numpy as np

from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_established_spouse_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    group_member_indices,
    has_parent_ids,
    household_has_parent_ids,
    household_member_indices,
    unlinked_parent,
)


def _allocation_parent_rows(person, period, first, second):
    """Resolve the co-resident parents and their spouses for allocation scope.

    Parent ids take precedence. Without ids, only unlinked parents enter
    the tax-unit proxy, together with their co-resident spouses, as in the
    existing SSI resource-deeming relationship contract.
    """
    linked = has_parent_ids(person, period)
    spouse = _ssi_established_spouse_indices(person, period, first, second)
    first_spouse = np.where(first >= 0, spouse[np.maximum(first, 0)], -1)
    second_spouse = np.where(second >= 0, spouse[np.maximum(second, 0)], -1)
    named = np.column_stack((first, second, first_spouse, second_spouse))
    rows = [np.where(linked[:, None], named, -1)]

    unlinked = unlinked_parent(person, period)
    parent_or_spouse = unlinked | ((spouse >= 0) & unlinked[np.maximum(spouse, 0)])
    households = person.household.reference_entity.members_entity_id
    tax_units = person.tax_unit.reference_entity.members_entity_id
    for member in group_member_indices(person.tax_unit):
        safe = np.maximum(member, 0)
        selected = (
            ~linked
            & (member >= 0)
            & (households[safe] == households)
            & parent_or_spouse[safe]
        )
        rows.append(np.where(selected, member, -1)[:, None])
        # A parent's spouse can file in a different tax unit.
        partner = np.where(selected, spouse[safe], -1)
        outside = (partner >= 0) & (tax_units[np.maximum(partner, 0)] != tax_units)
        rows.append(np.where(outside, partner, -1)[:, None])
    return np.column_stack(rows)


def ssi_parental_child_allocation_total(person, period, recipients):
    """Allocations for relevant children who live with this recipient.

    20 CFR 416.1165(b) limits allocations to ineligible children in the
    household. Parent ids identify a child of this person or their parents
    and parents' spouses; the unlinked-parent tax-unit proxy applies only
    where the parent-link contract permits it. A recipient never receives
    an allocation from the same pool of income they share.
    """
    first, second = co_resident_parent_indices(person, period)
    parents = _allocation_parent_rows(person, period, first, second)
    own_index = np.arange(person.count)
    relatives = np.column_stack((own_index, parents))
    present = relatives >= 0
    safe_relatives = np.maximum(relatives, 0)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    relative_tax_units = np.where(present, tax_unit[safe_relatives], -1)
    unlinked = unlinked_parent(person, period)
    may_presume = ~household_has_parent_ids(person, period) | np.any(
        present & unlinked[safe_relatives], axis=1
    )
    linked = has_parent_ids(person, period)
    allocation = person("ssi_ineligible_child_allocation", period)
    total = np.zeros(person.count)
    for child in household_member_indices(person):
        safe = np.maximum(child, 0)
        named = np.any(
            present
            & (
                (relatives == first[safe][:, None])
                | (relatives == second[safe][:, None])
            ),
            axis=1,
        )
        presumed = may_presume & np.any(
            present & (relative_tax_units == tax_unit[safe][:, None]), axis=1
        )
        is_parent = np.any(parents == child[:, None], axis=1)
        counts = (
            (child >= 0)
            & (child != own_index)
            & ~is_parent
            & ~recipients[safe]
            & np.where(linked[safe], named, presumed)
        )
        total += np.where(counts, allocation[safe], 0)
    return total
