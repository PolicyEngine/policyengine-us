from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    _parent_indices,
    co_resident_parent_indices,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


def _state_retained_pair(person, year):
    """A two-person marriage, excluding known parent/dependent pairs.

    Resolve parent links within the marital unit, including across households
    and tax units. A link naming a co-resident keeps that identity when the
    same id is reused by a spouse in another household. The existing parent
    resolver keeps its ambiguous-id fallback.
    As in SSI's spouse test, a possible default unit cannot make someone a
    spouse of the person who claims them as a tax dependent.
    """
    first, second = _parent_indices(person, year, person.marital_unit)
    home_first, home_second = co_resident_parent_indices(person, year)
    marital_unit = person.marital_unit.reference_entity.members_entity_id

    def prefer_co_resident(slot, home):
        in_unit = np.where(marital_unit[np.maximum(home, 0)] == marital_unit, home, -1)
        return np.where(home >= 0, in_unit, slot)

    first = prefer_co_resident(first, home_first)
    second = prefer_co_resident(second, home_second)
    parent_link = person.marital_unit.any((first >= 0) | (second >= 0))
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    same_tax_unit = person.marital_unit.min(tax_unit) == person.marital_unit.max(
        tax_unit
    )
    dependent_count = person.marital_unit.sum(person("is_tax_unit_dependent", year))
    claims = (person.marital_unit.count == 1) & same_tax_unit & (dependent_count == 1)
    return (person.marital_unit.nb_persons() == 2) & ~parent_link & ~claims


def state_couple_total(person, year, values):
    """Spouse totals for state rules that retain a declared marriage apart.

    A two-person marital unit declares the spouses unless parent/dependent
    facts rule them out, even when they occupy different households.
    Larger default groups instead use SSI's identified
    spouse pair, so an unrelated adult cannot enter the spouse's budget.
    Callers apply their own medical-separation, entry-month or care conditions;
    this helper does not change federal SSI's co-residence test.
    """
    return where(
        _state_retained_pair(person, year),
        person.marital_unit.sum(values),
        _ssi_couple_total(person, year, values),
    )


def state_is_married(person, year):
    """Declared spouses, including apart, or the identified default-group pair."""
    return _state_retained_pair(person, year) | (_ssi_spouse_index(person, year) >= 0)
