from policyengine_us.model_api import *
from policyengine_core.parameters import homogenize_parameter_structures
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.state_name import (
    StateName,
)
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    medicaid_rating_areas,
    second_lowest_silver_plan_cost,
)
import warnings

warnings.filterwarnings("ignore")

label = "Geography"


class state_name(Variable):
    value_type = Enum
    possible_values = StateName
    default_value = StateName.CA
    entity = Household
    label = "State"
    definition_period = YEAR

    def formula(household, period, parameters):
        fips = household("state_fips", period)
        return (
            pd.Series(fips)
            .map(
                {
                    1: StateName.AL,
                    2: StateName.AK,
                    4: StateName.AZ,
                    5: StateName.AR,
                    6: StateName.CA,
                    8: StateName.CO,
                    9: StateName.CT,
                    10: StateName.DE,
                    11: StateName.DC,
                    12: StateName.FL,
                    13: StateName.GA,
                    15: StateName.HI,
                    16: StateName.ID,
                    17: StateName.IL,
                    18: StateName.IN,
                    19: StateName.IA,
                    20: StateName.KS,
                    21: StateName.KY,
                    22: StateName.LA,
                    23: StateName.ME,
                    24: StateName.MD,
                    25: StateName.MA,
                    26: StateName.MI,
                    27: StateName.MN,
                    28: StateName.MS,
                    29: StateName.MO,
                    30: StateName.MT,
                    31: StateName.NE,
                    32: StateName.NV,
                    33: StateName.NH,
                    34: StateName.NJ,
                    35: StateName.NM,
                    36: StateName.NY,
                    37: StateName.NC,
                    38: StateName.ND,
                    39: StateName.OH,
                    40: StateName.OK,
                    41: StateName.OR,
                    42: StateName.PA,
                    44: StateName.RI,
                    45: StateName.SC,
                    46: StateName.SD,
                    47: StateName.TN,
                    48: StateName.TX,
                    49: StateName.UT,
                    50: StateName.VT,
                    51: StateName.VA,
                    53: StateName.WA,
                    54: StateName.WV,
                    55: StateName.WI,
                    56: StateName.WY,
                    72: StateName.PR,
                }
            )
            .values
        )


class medicaid_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Medicaid rating area"
    definition_period = YEAR
    hidden_input = True

    def formula(household, period, parameters):
        three_digit_zip_code = household("three_digit_zip_code", period)
        county = household("county_str", period)
        # Try a lookup on zip code, fill missing values with a lookup on county, fill missing with zero.
        df = pd.DataFrame(
            {
                "location": county,
            }
        )
        df_matched = pd.merge(
            df,
            medicaid_rating_areas,
            how="left",
            left_on="location",
            right_on="location",
        )
        county_lookup_failed = df_matched.rating_area.isna()
        df_matched.location[county_lookup_failed] = three_digit_zip_code[
            county_lookup_failed
        ]
        df_matched = pd.merge(
            df_matched,
            medicaid_rating_areas,
            how="left",
            left_on="location",
            right_on="location",
        )
        df_matched["rating_area"] = df_matched["rating_area_x"].fillna(
            df_matched["rating_area_y"]
        )
        return df_matched["rating_area"].fillna(1)


class county_fips(Variable):
    value_type = str
    label = "County FIPS code"
    entity = Household
    definition_period = YEAR
    documentation = "County FIPS code"


class state_fips(Variable):
    value_type = int
    label = "State FIPS code"
    entity = Household
    definition_period = YEAR
    documentation = "State FIPS code"
    default_value = 6


class congressional_district_geoid(Variable):
    value_type = int
    label = "Congressional district GEOID"
    entity = Household
    definition_period = YEAR
    documentation = """Congressional district geographic identifier stored as an integer.
    
    Format: SSDD where SS is the 2-digit state FIPS code and DD is the 2-digit district number.
    
    Examples:
    - Alabama (FIPS 01) district 01 is stored as 101
    - Alabama (FIPS 01) district 07 is stored as 107  
    - North Carolina (FIPS 37) district 01 is stored as 3701
    - California (FIPS 06) district 52 is stored as 652
    
    To extract components:
    - State FIPS: geoid // 100
    - District number: geoid % 100
    
    Note: Leading zeros are not preserved in the integer storage (e.g., 0101 becomes 101),
    but the value remains unique and unambiguous since the format is always interpreted as SSDD."""
    default_value = 0


class sldu(Variable):
    value_type = str
    label = "State Legislative District Upper"
    entity = Household
    definition_period = YEAR
    documentation = """State Legislative District Upper (State Senate district).

    This is a 3-character code from the Census Bureau's Block Assignment Files.
    Examples: "001", "002", "030".

    Empty string indicates the district is not assigned or unknown.

    Used for state-level policy analysis by state senate district."""
    default_value = ""


class sldl(Variable):
    value_type = str
    label = "State Legislative District Lower"
    entity = Household
    definition_period = YEAR
    documentation = """State Legislative District Lower (State Assembly/House district).

    This is a 3-character code from the Census Bureau's Block Assignment Files.
    Examples: "001", "002", "105".

    Empty string indicates the district is not assigned or unknown.
    Some states (e.g., Nebraska) have unicameral legislatures and lack SLDL.

    Used for state-level policy analysis by state assembly/house district."""
    default_value = ""


class block_geoid(Variable):
    value_type = str
    label = "Census Block GEOID"
    entity = Household
    definition_period = YEAR
    documentation = """15-digit Census Block Geographic Identifier.

    Format: SSCCCTTTTTTBBBB where:
    - SS = State FIPS (2 digits)
    - CCC = County FIPS (3 digits)
    - TTTTTT = Tract (6 digits)
    - BBBB = Block (4 digits)

    Example: "360610001001000" is a block in New York County (Manhattan), NY.

    All other geographic variables can be derived from block_geoid:
    - State FIPS: block_geoid[:2]
    - County FIPS: block_geoid[:5]
    - Tract GEOID: block_geoid[:11]

    Empty string indicates the block is not assigned."""
    default_value = ""


class tract_geoid(Variable):
    value_type = str
    label = "Census Tract GEOID"
    entity = Household
    definition_period = YEAR
    documentation = """11-digit Census Tract Geographic Identifier.

    Format: SSCCCTTTTTT where:
    - SS = State FIPS (2 digits)
    - CCC = County FIPS (3 digits)
    - TTTTTT = Tract (6 digits)

    Example: "36061000100" is a tract in New York County, NY.

    Empty string indicates the tract is not assigned."""
    default_value = ""


class cbsa_code(Variable):
    value_type = str
    label = "Core-Based Statistical Area (CBSA) Code"
    entity = Household
    definition_period = YEAR
    documentation = """5-digit CBSA code identifying the metropolitan or micropolitan area.

    CBSAs are defined by the Office of Management and Budget (OMB) and include:
    - Metropolitan Statistical Areas (population >= 50,000)
    - Micropolitan Statistical Areas (population 10,000-49,999)

    Example: "35620" is the New York-Newark-Jersey City metro area.

    Empty string indicates rural area (not in any CBSA)."""
    default_value = ""


class place_fips(Variable):
    value_type = str
    label = "Place FIPS Code"
    entity = Household
    definition_period = YEAR
    documentation = """5-digit Place FIPS code from Census Bureau.

    Places include incorporated places (cities, towns, villages) and
    Census Designated Places (CDPs) for unincorporated communities.

    Example: "51000" is New York City.

    Empty string indicates not in any Census place (unincorporated area)."""
    default_value = ""


class vtd(Variable):
    value_type = str
    label = "Voting Tabulation District"
    entity = Household
    definition_period = YEAR
    documentation = """Voting Tabulation District (VTD) code from Census Bureau.

    VTDs are election precincts or similar voting districts used for
    tabulating Census data on voting-age population.

    Empty string indicates VTD is not assigned or unknown."""
    default_value = ""


class puma(Variable):
    value_type = str
    label = "Public Use Microdata Area (PUMA)"
    entity = Household
    definition_period = YEAR
    documentation = """5-digit Public Use Microdata Area code from Census Bureau.

    PUMAs are the smallest geographic unit for which the Census Bureau
    releases individual records in the American Community Survey (ACS)
    and decennial census public use microdata samples (PUMS).

    Each PUMA contains at least 100,000 people.

    Example: "03201" is a PUMA in New York State.

    Empty string indicates PUMA is not assigned."""
    default_value = ""


class zcta(Variable):
    value_type = str
    label = "ZCTA (ZIP Code Tabulation Area)"
    entity = Household
    definition_period = YEAR
    documentation = """5-digit ZIP Code Tabulation Area from Census Bureau.

    ZCTAs are generalized areal representations of USPS ZIP Code service areas.
    They are built from Census blocks and do not precisely align with ZIP Codes,
    which are defined by mail delivery routes rather than geographic boundaries.

    Example: "10001" is a ZCTA in Manhattan, NY.

    Empty string indicates ZCTA is not assigned."""
    default_value = ""
