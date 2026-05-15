from policyengine_us.model_api import *


class AKCCAPRateRegion(Enum):
    ALEUTIANS_EAST = "Aleutians East Borough"
    ALEUTIANS_WEST = "Aleutians West Census Area"
    ANCHORAGE = "Municipality of Anchorage"
    BETHEL = "Bethel Census Area"
    BRISTOL_BAY = "Bristol Bay Borough"
    DENALI = "Denali Borough"
    DILLINGHAM = "Dillingham Census Area"
    FAIRBANKS_NORTH_STAR = "Fairbanks North Star Borough"
    HAINES = "Haines Borough"
    HOONAH_ANGOON = "Hoonah-Angoon Census Area"
    JUNEAU = "City and Borough of Juneau"
    KENAI_PENINSULA = "Kenai Peninsula Borough"
    KETCHIKAN_GATEWAY = "Ketchikan Gateway Borough"
    KODIAK_ISLAND = "Kodiak Island Borough"
    KUSILVAK = "Kusilvak Census Area"
    LAKE_AND_PENINSULA = "Lake and Peninsula Borough"
    MATANUSKA_SUSITNA = "Matanuska-Susitna Borough"
    NOME = "Nome Census Area"
    NORTH_SLOPE = "North Slope Borough"
    NORTHWEST_ARCTIC = "Northwest Arctic Borough"
    PETERSBURG = "Petersburg Borough"
    PRINCE_OF_WALES_HYDER = "Prince of Wales-Hyder Census Area"
    SITKA = "City and Borough of Sitka"
    SKAGWAY = "Skagway Municipality"
    SOUTHEAST_FAIRBANKS = "Southeast Fairbanks Census Area"
    VALDEZ_CORDOVA = "Valdez-Cordova Census Area"
    WRANGELL = "City and Borough of Wrangell"
    YAKUTAT = "Yakutat City and Borough"
    YUKON_KOYUKUK = "Yukon-Koyukuk Census Area"


# The 2019 split of the Valdez-Cordova Census Area into Chugach and
# Copper River successor counties is mapped back to the Valdez-Cordova
# rate column, which is still the one published on the rate schedule.
COUNTY_TO_REGION = {
    "ALEUTIANS_EAST_BOROUGH_AK": AKCCAPRateRegion.ALEUTIANS_EAST,
    "ALEUTIANS_WEST_CENSUS_AREA_AK": AKCCAPRateRegion.ALEUTIANS_WEST,
    "ANCHORAGE_MUNICIPALITY_AK": AKCCAPRateRegion.ANCHORAGE,
    "BETHEL_CENSUS_AREA_AK": AKCCAPRateRegion.BETHEL,
    "BRISTOL_BAY_BOROUGH_AK": AKCCAPRateRegion.BRISTOL_BAY,
    "CHUGACH_CENSUS_AREA_AK": AKCCAPRateRegion.VALDEZ_CORDOVA,
    "COPPER_RIVER_CENSUS_AREA_AK": AKCCAPRateRegion.VALDEZ_CORDOVA,
    "DENALI_BOROUGH_AK": AKCCAPRateRegion.DENALI,
    "DILLINGHAM_CENSUS_AREA_AK": AKCCAPRateRegion.DILLINGHAM,
    "FAIRBANKS_NORTH_STAR_BOROUGH_AK": AKCCAPRateRegion.FAIRBANKS_NORTH_STAR,
    "HAINES_BOROUGH_AK": AKCCAPRateRegion.HAINES,
    "HOONAH_ANGOON_CENSUS_AREA_AK": AKCCAPRateRegion.HOONAH_ANGOON,
    "JUNEAU_CITY_AND_BOROUGH_AK": AKCCAPRateRegion.JUNEAU,
    "KENAI_PENINSULA_BOROUGH_AK": AKCCAPRateRegion.KENAI_PENINSULA,
    "KETCHIKAN_GATEWAY_BOROUGH_AK": AKCCAPRateRegion.KETCHIKAN_GATEWAY,
    "KODIAK_ISLAND_BOROUGH_AK": AKCCAPRateRegion.KODIAK_ISLAND,
    "KUSILVAK_CENSUS_AREA_AK": AKCCAPRateRegion.KUSILVAK,
    "LAKE_AND_PENINSULA_BOROUGH_AK": AKCCAPRateRegion.LAKE_AND_PENINSULA,
    "MATANUSKA_SUSITNA_BOROUGH_AK": AKCCAPRateRegion.MATANUSKA_SUSITNA,
    "NOME_CENSUS_AREA_AK": AKCCAPRateRegion.NOME,
    "NORTH_SLOPE_BOROUGH_AK": AKCCAPRateRegion.NORTH_SLOPE,
    "NORTHWEST_ARCTIC_BOROUGH_AK": AKCCAPRateRegion.NORTHWEST_ARCTIC,
    "PETERSBURG_BOROUGH_AK": AKCCAPRateRegion.PETERSBURG,
    "PRINCE_OF_WALES_HYDER_CENSUS_AREA_AK": AKCCAPRateRegion.PRINCE_OF_WALES_HYDER,
    "SITKA_CITY_AND_BOROUGH_AK": AKCCAPRateRegion.SITKA,
    "SKAGWAY_MUNICIPALITY_AK": AKCCAPRateRegion.SKAGWAY,
    "SOUTHEAST_FAIRBANKS_CENSUS_AREA_AK": AKCCAPRateRegion.SOUTHEAST_FAIRBANKS,
    "WRANGELL_CITY_AND_BOROUGH_AK": AKCCAPRateRegion.WRANGELL,
    "YAKUTAT_CITY_AND_BOROUGH_AK": AKCCAPRateRegion.YAKUTAT,
    "YUKON_KOYUKUK_CENSUS_AREA_AK": AKCCAPRateRegion.YUKON_KOYUKUK,
}


class ak_ccap_rate_region(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = AKCCAPRateRegion
    default_value = AKCCAPRateRegion.ANCHORAGE
    definition_period = MONTH
    label = "Alaska CCAP rate region"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period.this_year)
        conditions = [county == name for name in COUNTY_TO_REGION]
        choices = list(COUNTY_TO_REGION.values())
        return select(conditions, choices, default=AKCCAPRateRegion.ANCHORAGE)
