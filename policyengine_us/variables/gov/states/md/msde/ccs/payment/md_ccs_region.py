from policyengine_us.model_api import *


class MDCCSRegion(Enum):
    REGION_U = "Region U"
    REGION_V = "Region V"
    REGION_W = "Region W"
    REGION_X = "Region X"
    REGION_Y = "Region Y"
    REGION_Z = "Region Z"
    BALTIMORE_CITY = "Baltimore City"


class md_ccs_region(Variable):
    value_type = Enum
    entity = Household
    # Non-MD households fall through to REGION_W; masked by defined_for on
    # consumers, but the load-bearing default is needed because vectorized
    # formula execution does not short-circuit on defined_for.
    possible_values = MDCCSRegion
    default_value = MDCCSRegion.REGION_W
    definition_period = MONTH
    defined_for = StateCode.MD
    label = "Maryland CCS rate region"
    reference = "https://earlychildhood.marylandpublicschools.org/families/child-care-scholarship-program/child-care-scholarship-rates"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.md.msde.ccs.payment
        is_region_u = np.isin(county, p.region_u_counties)
        is_region_v = np.isin(county, p.region_v_counties)
        is_region_w = np.isin(county, p.region_w_counties)
        is_region_x = np.isin(county, p.region_x_counties)
        is_region_y = np.isin(county, p.region_y_counties)
        is_region_z = np.isin(county, p.region_z_counties)
        is_baltimore_city = np.isin(county, p.baltimore_city_counties)
        return select(
            [
                is_region_u,
                is_region_v,
                is_region_w,
                is_region_x,
                is_region_y,
                is_region_z,
                is_baltimore_city,
            ],
            [
                MDCCSRegion.REGION_U,
                MDCCSRegion.REGION_V,
                MDCCSRegion.REGION_W,
                MDCCSRegion.REGION_X,
                MDCCSRegion.REGION_Y,
                MDCCSRegion.REGION_Z,
                MDCCSRegion.BALTIMORE_CITY,
            ],
            default=MDCCSRegion.REGION_W,
        )
