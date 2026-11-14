from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


def _spouse_filing_elsewhere(person, period, ineligible_parent):
    """Each person's spouse row, and whether it is a deeming spouse in another unit.

    20 CFR 416.1160(d): a parent's spouse who lives with the child is an
    ineligible parent too. When that spouse files in another tax unit, their
    income still joins the parent's (416.1165), as the couple rate in
    ssi_ineligible_parent_allocation assumes.
    """
    spouse = _ssi_spouse_index(person, period)
    safe_spouse = np.maximum(spouse, 0)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    elsewhere = (
        ineligible_parent
        & (spouse >= 0)
        & ineligible_parent[safe_spouse]
        & (tax_unit[safe_spouse] != tax_unit)
    )
    return safe_spouse, elsewhere


def _with_spouse_unit(person, safe_spouse, elsewhere, unit_values):
    """A tax unit's values plus those of the unit a deeming spouse files in.

    When spouses in two tax units pool their income, each unit deems the whole
    pool, so its eligible children and its ineligible children's allocations
    must include the other unit's: 416.1165(e)(2) divides "the parental income
    to be deemed equally among those eligible children", and 416.1165(b)
    allocates for "each ineligible child in the household".
    """
    return unit_values + person.tax_unit.sum(
        where(elsewhere, unit_values[safe_spouse], 0)
    )
