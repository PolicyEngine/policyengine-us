from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.income_limits import (
    lookup_sized_income_limit,
)
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)


def _enum_names(values):
    return np.asarray(
        [
            getattr(
                value,
                "name",
                str(value.decode() if isinstance(value, bytes) else value),
            )
            .split(".")[-1]
            .upper()
            .replace(" ", "_")
            for value in np.asarray(values, dtype=object)
        ]
    )


def housing_assistance_eligibility_from_income_limits(
    county_fips,
    annual_income,
    spm_unit_size,
    spm_unit_tenure_type,
    receives_housing_assistance,
    year: int,
):
    county_fips = np.asarray(county_fips)
    annual_income = np.asarray(annual_income)
    spm_unit_size = np.asarray(spm_unit_size)
    receives_housing_assistance = np.asarray(receives_housing_assistance, dtype=bool)
    extremely_low_limit = lookup_sized_income_limit(
        county_fips,
        spm_unit_size,
        year,
        "extremely_low_income",
    )
    very_low_limit = lookup_sized_income_limit(
        county_fips,
        spm_unit_size,
        year,
        "very_low_income",
    )
    low_limit = lookup_sized_income_limit(
        county_fips,
        spm_unit_size,
        year,
        "low_income",
    )
    is_income_eligible = (
        ((extremely_low_limit > 0) & (annual_income <= extremely_low_limit))
        | ((very_low_limit > 0) & (annual_income <= very_low_limit))
        | ((low_limit > 0) & (annual_income <= low_limit))
    )
    raw_tenure = np.asarray(spm_unit_tenure_type)
    if raw_tenure.dtype.kind in "OUS":
        is_renter = _enum_names(raw_tenure) == SPMUnitTenureType.RENTER.name
    else:
        is_renter = raw_tenure == SPMUnitTenureType.RENTER
    return receives_housing_assistance | (is_renter & is_income_eligible)


class is_eligible_for_housing_assistance(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is eligible for HUD voucher"
    documentation = "HUD housing assistance payment"
    definition_period = YEAR
    reference = "https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf"

    def formula(spm_unit, period, parameters):
        receives_housing_assistance = spm_unit("receives_housing_assistance", period)
        income_level = spm_unit("hud_income_level", period)
        income_levels = income_level.possible_values
        is_income_eligible = (
            (income_level == income_levels.ESPECIALLY_LOW)
            | (income_level == income_levels.VERY_LOW)
            | (income_level == income_levels.LOW)
        )
        tenure = spm_unit("spm_unit_tenure_type", period)
        is_renter = tenure == SPMUnitTenureType.RENTER
        return receives_housing_assistance | (is_renter & is_income_eligible)
