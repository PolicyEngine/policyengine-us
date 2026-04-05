from policyengine_us.model_api import *


class SnapUtilityRegion(Enum):
    AL = "AL"
    AK_C = "AK_C"
    AK_N = "AK_N"
    AK_NW = "AK_NW"
    AK_SC = "AK_SC"
    AK_SE = "AK_SE"
    AK_SW = "AK_SW"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY_NAS = "NY_NAS"
    NY_NYC = "NY_NYC"
    NY_ONY = "NY_ONY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"
    DC = "DC"
    GU = "GU"
    MP = "MP"
    PW = "PW"
    PR = "PR"
    VI = "VI"
    AA = "AA"
    AE = "AE"
    AP = "AP"


# Alaska county-to-region mapping per 7 AAC 45.531
AK_CENTRAL = [
    "ANCHORAGE_MUNICIPALITY_AK",
    "MATANUSKA_SUSITNA_BOROUGH_AK",
]
AK_NORTHERN = [
    "COPPER_RIVER_CENSUS_AREA_AK",
    "DENALI_BOROUGH_AK",
    "FAIRBANKS_NORTH_STAR_BOROUGH_AK",
    "NORTH_SLOPE_BOROUGH_AK",
    "SOUTHEAST_FAIRBANKS_CENSUS_AREA_AK",
    "YUKON_KOYUKUK_CENSUS_AREA_AK",
]
AK_NORTHWEST = [
    "NOME_CENSUS_AREA_AK",
    "NORTHWEST_ARCTIC_BOROUGH_AK",
]
AK_SOUTHCENTRAL = [
    "ALEUTIANS_EAST_BOROUGH_AK",
    "ALEUTIANS_WEST_CENSUS_AREA_AK",
    "CHUGACH_CENSUS_AREA_AK",
    "KENAI_PENINSULA_BOROUGH_AK",
    "KODIAK_ISLAND_BOROUGH_AK",
]
AK_SOUTHEAST = [
    "HAINES_BOROUGH_AK",
    "JUNEAU_CITY_AND_BOROUGH_AK",
    "KETCHIKAN_GATEWAY_BOROUGH_AK",
    "PETERSBURG_BOROUGH_AK",
    "SITKA_CITY_AND_BOROUGH_AK",
    "HOONAH_ANGOON_CENSUS_AREA_AK",
    "PRINCE_OF_WALES_HYDER_CENSUS_AREA_AK",
    "SKAGWAY_MUNICIPALITY_AK",
    "WRANGELL_CITY_AND_BOROUGH_AK",
    "YAKUTAT_CITY_AND_BOROUGH_AK",
]
AK_SOUTHWEST = [
    "BETHEL_CENSUS_AREA_AK",
    "BRISTOL_BAY_BOROUGH_AK",
    "DILLINGHAM_CENSUS_AREA_AK",
    "KUSILVAK_CENSUS_AREA_AK",
    "LAKE_AND_PENINSULA_BOROUGH_AK",
]

# Build reverse lookup: county_str -> region code
AK_COUNTY_TO_REGION = {
    county: region
    for counties, region in [
        (AK_CENTRAL, "AK_C"),
        (AK_NORTHERN, "AK_N"),
        (AK_NORTHWEST, "AK_NW"),
        (AK_SOUTHCENTRAL, "AK_SC"),
        (AK_SOUTHEAST, "AK_SE"),
        (AK_SOUTHWEST, "AK_SW"),
    ]
    for county in counties
}

# New York county-to-region mapping
NY_COUNTY_TO_REGION = {
    county: region
    for counties, region in [
        (
            [
                "BRONX_COUNTY_NY",
                "KINGS_COUNTY_NY",
                "NEW_YORK_COUNTY_NY",
                "QUEENS_COUNTY_NY",
                "RICHMOND_COUNTY_NY",
            ],
            "NY_NYC",
        ),
        (
            [
                "NASSAU_COUNTY_NY",
                "SUFFOLK_COUNTY_NY",
            ],
            "NY_NAS",
        ),
    ]
    for county in counties
}


class snap_utility_region(Variable):
    value_type = Enum
    possible_values = SnapUtilityRegion
    default_value = SnapUtilityRegion.CA
    entity = Household
    label = "SNAP utility region"
    documentation = (
        "Region deciding the SNAP utility allowances. "
        "Most states have a single region, but Alaska has 6 "
        "and New York has 3 sub-regions."
    )
    definition_period = YEAR

    def formula(household, period, parameters):
        state_code = household("state_code", period).decode_to_str()
        county_str = household("county_str", period)

        # Default: use state code as region
        region = state_code

        # Alaska: map county to one of 6 sub-regions
        is_ak = state_code == "AK"
        if is_ak.any():
            for county_name, ak_region in AK_COUNTY_TO_REGION.items():
                region = where(
                    is_ak & (county_str == county_name),
                    ak_region,
                    region,
                )
            # Default AK counties not in mapping to Central
            still_ak = is_ak & (region == "AK")
            region = where(still_ak, "AK_C", region)

        # New York: map county to one of 3 sub-regions
        is_ny = state_code == "NY"
        if is_ny.any():
            for county_name, ny_region in NY_COUNTY_TO_REGION.items():
                region = where(
                    is_ny & (county_str == county_name),
                    ny_region,
                    region,
                )
            # Default NY counties not in mapping to Other NY
            still_ny = is_ny & (region == "NY")
            region = where(still_ny, "NY_ONY", region)

        return region
