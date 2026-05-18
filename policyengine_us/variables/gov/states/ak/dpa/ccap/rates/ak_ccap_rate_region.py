from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class ak_ccap_rate_region(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = County
    default_value = County.ANCHORAGE_MUNICIPALITY_AK
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
            County.CHUGACH_CENSUS_AREA_AK.name,
            county,
        )
        # Households with missing county data fall back to Anchorage so
        # the downstream rate lookup always hits a valid AK borough key.
        rate_region = where(
            rate_region == County.UNKNOWN.name,
            County.ANCHORAGE_MUNICIPALITY_AK.name,
            rate_region,
        )
        return County.encode(rate_region)
