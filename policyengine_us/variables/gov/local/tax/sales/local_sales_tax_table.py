from policyengine_us.model_api import *
from policyengine_us.tools.local_sales_tax_geography import sales_tax_location


class LocalSalesTaxTable(Enum):
    A = "Local Table A"
    B = "Local Table B"
    C = "Local Table C"
    D = "Local Table D"
    NONE = "No local table"


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
        "that impose a local sales tax. NONE signals an absent table, including "
        "Mississippi outside Jackson and Tupelo. Cities and counties are read from "
        "place_fips and county_fips, with the same block, explicit county, "
        "city-flag and principal-county fallbacks as combined_sales_tax_rate."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=16",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=18",
    )

    def formula(household, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.local_sales_tax_table
        location = sales_tax_location(household, period)
        state_code = location.state_code.to_numpy()
        county_fips = location.county_fips.to_numpy()
        place_geoid = location.place_geoid.to_numpy()
        # Named cities take precedence over their county, including Atlanta
        # within the selector's "DeKalb County (excluding Atlanta)" row.
        tables = [
            LocalSalesTaxTable.A,
            LocalSalesTaxTable.B,
            LocalSalesTaxTable.C,
            LocalSalesTaxTable.D,
        ]
        letters = ["a", "b", "c", "d"]
        default_letters = letters + ["none"]
        return select(
            [np.isin(place_geoid, p.place[letter]) for letter in letters]
            + [np.isin(county_fips, p.county[letter]) for letter in letters]
            + [
                np.isin(state_code, p.default_table[letter])
                for letter in default_letters
            ],
            tables * 3 + [LocalSalesTaxTable.NONE],
            default=LocalSalesTaxTable.A,
        )
