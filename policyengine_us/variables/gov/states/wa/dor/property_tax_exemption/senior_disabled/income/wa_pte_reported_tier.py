from functools import lru_cache

from policyengine_us.model_api import *
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    map_county_string_to_enum,
)
from policyengine_us.variables.gov.states.wa.dor.property_tax_exemption.senior_disabled.income.wa_pte_reported_combined_disposable_income import (
    UNREPORTED_COMBINED_DISPOSABLE_INCOME,
)
from policyengine_us.variables.gov.states.wa.dor.property_tax_exemption.senior_disabled.income.wa_pte_tier import (
    property_tax_exemption_tier,
)
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


@lru_cache(maxsize=1)
def washington_counties_by_fips():
    counties = load_county_fips_dataset()
    washington_counties = counties.loc[counties["state"] == "WA"]
    indices = map_county_string_to_enum(
        washington_counties["county_name"],
        washington_counties["state"],
    )
    return pd.Series(
        np.asarray(County._member_names_)[indices.to_numpy()],
        index=washington_counties["county_fips"],
    )


class wa_pte_reported_tier(Variable):
    value_type = int
    entity = TaxUnit
    label = (
        "Washington senior property tax exemption tier using reported assessment facts"
    )
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Session%20Laws/House/1355-S.SL.htm",
        "https://dor.wa.gov/sites/default/files/2023-08/Income_ThreshTY24-26.pdf",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.dor.property_tax_exemption.senior_disabled
        if not p.reported_regular_exemption_in_effect:
            return 0

        person = tax_unit.members
        age = person("wa_pte_assessment_year_age", period)
        head = person("is_tax_unit_head", period)
        # The shared age parameter is expressed at the end of the collection year.
        senior_claimant = tax_unit.any(
            head & np.isfinite(age) & (age >= p.age_threshold - 1)
        )
        single_occupant = tax_unit.household("household_size", period) == 1
        owner_occupant = tax_unit("wa_pte_owner_occupant", period)
        assessed_value = tax_unit("wa_pte_assessor_approved_value", period)
        income = tax_unit("wa_pte_reported_combined_disposable_income", period)
        has_reported_income = np.isfinite(income) & (
            income != UNREPORTED_COMBINED_DISPOSABLE_INCOME
        )

        # Resolve the report itself. The general county variable can use a
        # population fallback when the input is missing or unrecognized.
        fips = tax_unit.household("county_fips", period).astype(str)
        reported_county = washington_counties_by_fips().reindex(fips)
        county_known = reported_county.notna().to_numpy()
        # Give the vectorized lookup a valid key for rows the result masks out.
        county = reported_county.fillna("ADAMS_COUNTY_WA").to_numpy()
        tier = property_tax_exemption_tier(income, county, p.income.thresholds)
        has_approved_value = np.isfinite(assessed_value) & (assessed_value >= 0)
        valid_claim = (
            senior_claimant
            & single_occupant
            & owner_occupant
            & has_approved_value
            & has_reported_income
            & county_known
        )
        return where(valid_claim, tier, 0)
