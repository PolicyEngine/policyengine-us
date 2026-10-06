from policyengine_us.model_api import *
from policyengine_us.tools.geography.county_helpers import (
    state_fips_by_state_code,
)


class LocalSalesTaxTable(Enum):
    A = "Local Table A"
    B = "Local Table B"
    C = "Local Table C"
    D = "Local Table D"


class local_sales_tax_table(Variable):
    value_type = Enum
    possible_values = LocalSalesTaxTable
    default_value = LocalSalesTaxTable.A
    entity = Household
    definition_period = YEAR
    label = "IRS Optional Local Sales Tax Table"
    documentation = (
        "The IRS Optional Local Sales Tax Table for the household's locality, from "
        "the IRS table selector: the table of the household's city if the selector "
        "names it, else of its county, else the state's table for other localities "
        "that impose a local sales tax. Cities and counties are read from "
        "place_fips and county_fips."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sca--2015.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2016.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2017.pdf#page=19",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2018.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2019.pdf#page=19",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2020.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2021.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=16",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=18",
    )

    def formula(household, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.local_sales_tax_table
        state_code = household("state_code_str", period)
        # The selector names some counties and cities. A named city's row
        # takes precedence over its county's row, as in "Dekalb County
        # (excluding Atlanta)". Keys are FIPS codes, never the county enum,
        # which falls back to the state's alphabetically first county.
        state_fips = (
            pd.Series(state_code).map(state_fips_by_state_code()).fillna("").to_numpy()
        )
        county_fips = pd.Series(household("county_fips", period)).astype(str)
        county_fips = county_fips.where(
            county_fips == "", county_fips.str.zfill(5)
        ).to_numpy()
        place_fips = pd.Series(household("place_fips", period)).astype(str)
        # Accept a 7-digit place GEOID (state FIPS code and place code).
        place_fips = place_fips.where(place_fips.str.len() != 7, place_fips.str[2:])
        place_fips = place_fips.where(place_fips == "", place_fips.str.zfill(5))
        place_geoid = where(place_fips != "", state_fips + place_fips.to_numpy(), "")
        county_in_state = pd.Series(county_fips).str[:2].to_numpy() == state_fips
        county_fips = where(county_in_state, county_fips, "")
        tables = [
            LocalSalesTaxTable.A,
            LocalSalesTaxTable.B,
            LocalSalesTaxTable.C,
            LocalSalesTaxTable.D,
        ]
        letters = ["a", "b", "c", "d"]
        return select(
            [np.isin(place_geoid, p.place[letter]) for letter in letters]
            + [np.isin(county_fips, p.county[letter]) for letter in letters]
            + [np.isin(state_code, p.default_table[letter]) for letter in letters],
            tables * 3,
            default=LocalSalesTaxTable.A,
        )
