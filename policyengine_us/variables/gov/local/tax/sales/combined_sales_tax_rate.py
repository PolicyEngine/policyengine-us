from policyengine_us.model_api import *
from policyengine_us.tools.local_sales_tax_rates import locality_sales_tax_rates


class combined_sales_tax_rate(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "/1"
    label = "Combined state and local general sales tax rate"
    documentation = (
        "The combined state and local general sales tax rate where the household "
        "lives. In New York, Virginia and the Streamlined Sales Tax states with "
        "local sales taxes, it is the official rate of the household's place, or "
        "of its county's area outside the places with their own rate, from the "
        "states' rate files; with only the county known, the county's "
        "population-weighted rate; and with no county, the state's. Elsewhere "
        "PolicyEngine has no official locality rates and uses the state rate in "
        "the IRS state table heading, so the local general sales tax rate is 0. "
        "Enter the household's combined rate to use it instead."
    )
    reference = (
        "https://www.streamlinedsalestax.org/Shared-Pages/rate-and-boundary-files",
        "https://www.tax.ny.gov/pdf/publications/sales/pub718.pdf",
        "https://www.tax.virginia.gov/sites/default/files/inline-files/sales-and-use-tax-rates-by-locality-by-date.xlsx",
    )

    def formula(household, period, parameters):
        rates = locality_sales_tax_rates(period.start.year)
        state = pd.Series(household("state_code_str", period)).astype(str)
        county = pd.Series(household("county_fips", period)).astype(str)
        county = county.where(county == "", county.str.zfill(5))
        place = pd.Series(household("place_fips", period)).astype(str)
        place = place.where(place == "", place.str.zfill(5))
        block = pd.Series(household("block_geoid", period)).astype(str)
        # Locality rates are keyed on FIPS codes, never on the county enum,
        # which falls back to the state's alphabetically first county. A
        # county outside the household's state is ignored.
        county = county.where(county.map(rates.county_state) == state, "")
        place_rate = (county + place).map(rates.place)
        # A known place without its own rate, or a known census block outside
        # every place (an empty place code), is in its county's area outside
        # those places. With only the county known, use the county's rate.
        location_known = (place != "") | (block != "")
        county_rate = county.map(rates.outside_places).where(location_known)
        county_rate = county_rate.fillna(county.map(rates.county))
        official = place_rate.fillna(county_rate).fillna(state.map(rates.state))
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        heading_rate = p.state_sales_tax_table.rate[household("state_code", period)]
        return where(official.isna().to_numpy(), heading_rate, official.to_numpy())
