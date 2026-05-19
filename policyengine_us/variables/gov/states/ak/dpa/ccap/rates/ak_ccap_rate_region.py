from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class AKCCAPRateRegion(Enum):
    ALEUTIANS_EAST_BOROUGH_AK = "Aleutians East Borough"
    ALEUTIANS_WEST_CENSUS_AREA_AK = "Aleutians West Census Area"
    ANCHORAGE_MUNICIPALITY_AK = "Anchorage Municipality"
    BETHEL_CENSUS_AREA_AK = "Bethel Census Area"
    BRISTOL_BAY_BOROUGH_AK = "Bristol Bay Borough"
    CHUGACH_CENSUS_AREA_AK = "Chugach Census Area"
    DENALI_BOROUGH_AK = "Denali Borough"
    DILLINGHAM_CENSUS_AREA_AK = "Dillingham Census Area"
    FAIRBANKS_NORTH_STAR_BOROUGH_AK = "Fairbanks North Star Borough"
    HAINES_BOROUGH_AK = "Haines Borough"
    HOONAH_ANGOON_CENSUS_AREA_AK = "Hoonah-Angoon Census Area"
    JUNEAU_CITY_AND_BOROUGH_AK = "Juneau City and Borough"
    KENAI_PENINSULA_BOROUGH_AK = "Kenai Peninsula Borough"
    KETCHIKAN_GATEWAY_BOROUGH_AK = "Ketchikan Gateway Borough"
    KODIAK_ISLAND_BOROUGH_AK = "Kodiak Island Borough"
    KUSILVAK_CENSUS_AREA_AK = "Kusilvak Census Area"
    LAKE_AND_PENINSULA_BOROUGH_AK = "Lake and Peninsula Borough"
    MATANUSKA_SUSITNA_BOROUGH_AK = "Matanuska-Susitna Borough"
    NOME_CENSUS_AREA_AK = "Nome Census Area"
    NORTH_SLOPE_BOROUGH_AK = "North Slope Borough"
    NORTHWEST_ARCTIC_BOROUGH_AK = "Northwest Arctic Borough"
    PETERSBURG_BOROUGH_AK = "Petersburg Borough"
    PRINCE_OF_WALES_HYDER_CENSUS_AREA_AK = "Prince of Wales-Hyder Census Area"
    SITKA_CITY_AND_BOROUGH_AK = "Sitka City and Borough"
    SKAGWAY_MUNICIPALITY_AK = "Skagway Municipality"
    SOUTHEAST_FAIRBANKS_CENSUS_AREA_AK = "Southeast Fairbanks Census Area"
    WRANGELL_CITY_AND_BOROUGH_AK = "Wrangell City and Borough"
    YAKUTAT_CITY_AND_BOROUGH_AK = "Yakutat City and Borough"
    YUKON_KOYUKUK_CENSUS_AREA_AK = "Yukon-Koyukuk Census Area"


class ak_ccap_rate_region(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = AKCCAPRateRegion
    default_value = AKCCAPRateRegion.ANCHORAGE_MUNICIPALITY_AK
    definition_period = MONTH
    label = "Alaska CCAP rate region"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period.this_year)
        # The 2019 split of the Valdez-Cordova Census Area produced two
        # successors (Chugach and Copper River); the rate schedule still
        # publishes one combined Valdez-Cordova column, so we collapse
        # Copper River into Chugach to share that single rate.
        rate_region = where(
            county == County.COPPER_RIVER_CENSUS_AREA_AK.name,
            AKCCAPRateRegion.CHUGACH_CENSUS_AREA_AK.name,
            county,
        )
        # Fall back to Anchorage when the county string is UNKNOWN or
        # any other value not in the AK rate-region enum.
        valid_region_names = [r.name for r in AKCCAPRateRegion]
        is_valid = np.isin(rate_region, valid_region_names)
        rate_region = where(
            is_valid,
            rate_region,
            AKCCAPRateRegion.ANCHORAGE_MUNICIPALITY_AK.name,
        )
        return AKCCAPRateRegion.encode(rate_region)
