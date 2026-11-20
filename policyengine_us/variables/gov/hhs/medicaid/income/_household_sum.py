"""Sum a value over each person's Medicaid MAGI household."""

import numpy as np

from policyengine_us.model_api import where
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    medicaid_claiming_tax_unit_value,
    medicaid_external_claimed_sum,
)
from policyengine_us.variables.gov.hhs.medicaid.income._non_filer_household import (
    medicaid_filer_spouse_sum,
    medicaid_non_filer_fallback_sum,
    medicaid_non_filer_member_sum,
    medicaid_tax_dependent_spouse_sum,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    household_has_parent_ids,
)


def medicaid_household_sum(
    person, period, values, spouse_values, separate_spouse_values
):
    """Sum ``values`` once over each person's MAGI household.

    Tax filers and tax dependents follow the tax household (42 CFR
    435.603(f)(1), (f)(2) and (f)(4)); people under the non-filer rules
    follow (f)(3). medicaid_household_size counts members with ``values`` of
    one, and medicaid_household_pregnancies sums each member's counted
    expected children. ``spouse_values`` is what the non-filer household's
    spouse adds (medicaid_non_filer_fallback_sum's ``spouse_sum``), and
    ``separate_spouse_values`` is what a separately filing spouse adds to
    every member of the tax household when the tax unit flags cohabiting
    spouses.
    """
    values = np.asarray(values, dtype=np.float64)
    has_parent_ids = household_has_parent_ids(person, period)
    non_filer = where(
        has_parent_ids,
        medicaid_non_filer_member_sum(person, period, values),
        medicaid_non_filer_fallback_sum(person, period, values, spouse_values),
    )
    # With parent links, a head's or spouse's co-resident spouse outside the
    # unit joins the unit's tax household, which its dependents and claimants
    # elsewhere share (42 CFR 435.603(f)(2) and (f)(4)).
    tax_household = (
        person.tax_unit.sum(values)
        + separate_spouse_values
        + person.tax_unit.sum(medicaid_filer_spouse_sum(person, period, values))
        + medicaid_external_claimed_sum(
            person, period, person.tax_unit("tax_unit_id", period), values
        )
    )
    tax_route = where(
        person("medicaid_has_known_claiming_tax_unit", period),
        medicaid_claiming_tax_unit_value(person, period, tax_household),
        tax_household,
    )
    # With parent links, a tax dependent's co-resident spouse joins their tax
    # household once (42 CFR 435.603(f)(4)).
    tax_route = where(
        has_parent_ids,
        tax_route + medicaid_tax_dependent_spouse_sum(person, period, values),
        tax_route,
    )
    return where(person("medicaid_uses_non_filer_rules", period), non_filer, tax_route)
