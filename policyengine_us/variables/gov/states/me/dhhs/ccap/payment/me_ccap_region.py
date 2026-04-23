from datetime import date

from policyengine_us.model_api import *


class MECCAPRegion(Enum):
    ANDROSCOGGIN = "Androscoggin"
    AROOSTOOK = "Aroostook"
    CUMBERLAND = "Cumberland"
    FRANKLIN = "Franklin"
    HANCOCK = "Hancock"
    REGION_1 = "Region 1"
    REGION_2 = "Region 2"
    KENNEBEC = "Kennebec"
    KNOX = "Knox"
    KNOX_WALDO = "Knox/Waldo"
    LINCOLN = "Lincoln"
    OXFORD = "Oxford"
    PENOBSCOT = "Penobscot"
    PISCATAQUIS = "Piscataquis"
    SAGADAHOC = "Sagadahoc"
    SOMERSET = "Somerset"
    WALDO = "Waldo"
    WASHINGTON = "Washington"
    YORK = "York"


class me_ccap_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = MECCAPRegion
    default_value = MECCAPRegion.REGION_2
    definition_period = MONTH
    defined_for = StateCode.ME
    label = "Maine CCAP geographic region"
    reference = (
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/2021%20Maine%20Market%20Rate%207-3-21_0.pdf",
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=25",
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/July%206%202024%20Market%20Rates_5_0.pdf",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)

        if period.start.date < date(2024, 7, 6):
            return select(
                [
                    county == "ANDROSCOGGIN_COUNTY_ME",
                    county == "AROOSTOOK_COUNTY_ME",
                    county == "CUMBERLAND_COUNTY_ME",
                    county == "FRANKLIN_COUNTY_ME",
                    county == "HANCOCK_COUNTY_ME",
                    county == "KENNEBEC_COUNTY_ME",
                    county == "KNOX_COUNTY_ME",
                    county == "LINCOLN_COUNTY_ME",
                    county == "OXFORD_COUNTY_ME",
                    county == "PENOBSCOT_COUNTY_ME",
                    county == "PISCATAQUIS_COUNTY_ME",
                    county == "SAGADAHOC_COUNTY_ME",
                    county == "SOMERSET_COUNTY_ME",
                    county == "WALDO_COUNTY_ME",
                    county == "WASHINGTON_COUNTY_ME",
                    county == "YORK_COUNTY_ME",
                ],
                [
                    MECCAPRegion.ANDROSCOGGIN,
                    MECCAPRegion.AROOSTOOK,
                    MECCAPRegion.CUMBERLAND,
                    MECCAPRegion.FRANKLIN,
                    MECCAPRegion.HANCOCK,
                    MECCAPRegion.KENNEBEC,
                    MECCAPRegion.KNOX,
                    MECCAPRegion.LINCOLN,
                    MECCAPRegion.OXFORD,
                    MECCAPRegion.PENOBSCOT,
                    MECCAPRegion.PISCATAQUIS,
                    MECCAPRegion.SAGADAHOC,
                    MECCAPRegion.SOMERSET,
                    MECCAPRegion.WALDO,
                    MECCAPRegion.WASHINGTON,
                    MECCAPRegion.YORK,
                ],
                default=MECCAPRegion.AROOSTOOK,
            )

        p = parameters(period).gov.states.me.dhhs.ccap
        is_region_1 = np.isin(county, p.region_1_counties)
        is_kennebec = np.isin(county, p.kennebec_counties)
        is_knox_waldo = np.isin(county, p.knox_waldo_counties)
        is_penobscot = np.isin(county, p.penobscot_counties)
        return select(
            [is_region_1, is_kennebec, is_knox_waldo, is_penobscot],
            [
                MECCAPRegion.REGION_1,
                MECCAPRegion.KENNEBEC,
                MECCAPRegion.KNOX_WALDO,
                MECCAPRegion.PENOBSCOT,
            ],
            default=MECCAPRegion.REGION_2,
        )
