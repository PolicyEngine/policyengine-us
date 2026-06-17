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
        # The CCDF State Plan rate table reports two regions: the most populous
        # region (Clark County) and the lowest-percentile region (every other
        # county). `county_str` is a Household accessor enumerating every US
        # county, so non-Nevada county strings flow through this formula in
        # microsim even though `defined_for` filters the output. Comparing the
        # county string directly (rather than indexing a parameter by it) keeps
        # the lookup safe for any county value.
        county = person.household("county_str", period.this_year)
        return where(
            county == "CLARK_COUNTY_NV",
            NVCCDPRegion.MOST_POPULOUS,
            NVCCDPRegion.LOWEST_PERCENTILE,
        )
