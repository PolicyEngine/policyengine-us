from policyengine_us.model_api import *


class NVCCDPRegion(Enum):
    MOST_POPULOUS = "Most populous region (Clark County)"
    LOWEST_PERCENTILE = "Lowest-percentile region (all other counties)"


class nv_ccdp_region(Variable):
    value_type = Enum
    entity = Person
    possible_values = NVCCDPRegion
    default_value = NVCCDPRegion.LOWEST_PERCENTILE
    definition_period = MONTH
    label = "Nevada CCDP reimbursement-rate region"
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/ACF-118_CCDF_FFY_2025-2027_For_Nevada__3.pdf#page=54"

    def formula(person, period, parameters):
        # The Policy Manual MS 633.2 publishes Licensed Provider rates for four
        # areas (Clark, Washoe, Carson-Douglas, Rural) across QRIS star tiers
        # 1-5. We collapse this to two modeled regions: the most populous region
        # (Clark County) and a lowest-percentile region that applies the Washoe
        # 1-Star rates as the representative for every other county. This applies
        # the Washoe-level rate to Carson-Douglas and rural counties (whose
        # Manual rates are lower) and does not track star-level rate
        # enhancements at the moment.
        # `county_str` is a Household accessor enumerating every US county, so
        # non-Nevada county strings flow through this formula in microsim even
        # though `defined_for` filters the output. Comparing the county string
        # directly (rather than indexing a parameter by it) keeps the lookup
        # safe for any county value.
        county = person.household("county_str", period.this_year)
        return where(
            county == "CLARK_COUNTY_NV",
            NVCCDPRegion.MOST_POPULOUS,
            NVCCDPRegion.LOWEST_PERCENTILE,
        )
