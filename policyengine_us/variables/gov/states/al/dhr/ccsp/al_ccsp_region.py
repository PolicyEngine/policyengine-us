from policyengine_us.model_api import *


class ALCCSPRegion(Enum):
    HUNTSVILLE = "Huntsville"
    TUSCALOOSA = "Tuscaloosa"
    MOBILE = "Mobile"
    FT_PAYNE = "Ft. Payne"
    BIRMINGHAM = "Birmingham"
    TALLADEGA = "Talladega"
    MONTGOMERY = "Montgomery"
    DOTHAN = "Dothan"
    OPELIKA = "Opelika"


class al_ccsp_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = ALCCSPRegion
    default_value = ALCCSPRegion.BIRMINGHAM
    definition_period = YEAR
    label = "Alabama CCSP rate-setting region"
    defined_for = StateCode.AL
    reference = (
        "Alabama DHR Provider Rate Chart, Regions and Counties Served",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/Provider-Rates-with-QRIS-Tiers-April-1-2022-b.pdf#page=1",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        state = household("state_code_str", period)
        # Mask with state_code_str == "AL" so non-Alabama county strings
        # do not flow into the region lookup (defined_for filters output
        # but does not short-circuit vectorized indexing).
        in_alabama = state == "AL"
        p = parameters(period).gov.states.al.dhr.ccsp.region.counties
        return select(
            [
                in_alabama & np.isin(county, p.HUNTSVILLE),
                in_alabama & np.isin(county, p.TUSCALOOSA),
                in_alabama & np.isin(county, p.MOBILE),
                in_alabama & np.isin(county, p.FT_PAYNE),
                in_alabama & np.isin(county, p.BIRMINGHAM),
                in_alabama & np.isin(county, p.TALLADEGA),
                in_alabama & np.isin(county, p.MONTGOMERY),
                in_alabama & np.isin(county, p.DOTHAN),
                in_alabama & np.isin(county, p.OPELIKA),
            ],
            [
                ALCCSPRegion.HUNTSVILLE,
                ALCCSPRegion.TUSCALOOSA,
                ALCCSPRegion.MOBILE,
                ALCCSPRegion.FT_PAYNE,
                ALCCSPRegion.BIRMINGHAM,
                ALCCSPRegion.TALLADEGA,
                ALCCSPRegion.MONTGOMERY,
                ALCCSPRegion.DOTHAN,
                ALCCSPRegion.OPELIKA,
            ],
            default=ALCCSPRegion.BIRMINGHAM,
        )
