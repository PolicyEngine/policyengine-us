from policyengine_us.model_api import *


class SDCCARegion(Enum):
    URBAN = "Urban"
    SUBURBAN = "Suburban"
    RURAL = "Rural"


class sd_cca_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = SDCCARegion
    # The 46 counties that are neither urban nor suburban (and any non-South
    # Dakota county) fall through to the rural region. This default is
    # load-bearing because defined_for does not short-circuit vectorized
    # formula execution.
    default_value = SDCCARegion.RURAL
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA provider rate region"
    reference = "https://dss.sd.gov/docs/childcare/assistance/Provider_Rate_Regions.pdf"

    def formula(household, period, parameters):
        county = household("county_str", period.this_year)
        p = parameters(period).gov.states.sd.dss.cca.rates
        return select(
            [
                np.isin(county, p.urban_counties),
                np.isin(county, p.suburban_counties),
            ],
            [SDCCARegion.URBAN, SDCCARegion.SUBURBAN],
            default=SDCCARegion.RURAL,
        )
