from policyengine_us.model_api import *


class VACCSPReadyRegion(Enum):
    BLUE_RIDGE = "Blue Ridge"
    CAPITAL_AREA = "Capital Area"
    CENTRAL = "Central"
    CHESAPEAKE_BAY = "Chesapeake Bay"
    NORTH_CENTRAL = "North Central"
    SOUTHEASTERN = "Southeastern"
    SOUTHSIDE = "Southside"
    SOUTHWEST = "Southwest"
    WEST = "West"


class va_ccsp_ready_region(Variable):
    value_type = Enum
    possible_values = VACCSPReadyRegion
    default_value = VACCSPReadyRegion.CENTRAL
    entity = Household
    definition_period = YEAR
    label = "Virginia CCSP Ready Region"
    defined_for = StateCode.VA
    reference = "https://data.virginia.gov/dataset/general-child-care-subsidy-program-maximum-reimbursement-rates"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(
            period
        ).gov.states.va.dss.ccsp.maximum_reimbursement_rate.ready_region

        blue_ridge = np.isin(county, p.blue_ridge)
        capital_area = np.isin(county, p.capital_area)
        central = np.isin(county, p.central)
        chesapeake_bay = np.isin(county, p.chesapeake_bay)
        north_central = np.isin(county, p.north_central)
        southeastern = np.isin(county, p.southeastern)
        southside = np.isin(county, p.southside)
        southwest = np.isin(county, p.southwest)
        west = np.isin(county, p.west)

        return select(
            [
                blue_ridge,
                capital_area,
                central,
                chesapeake_bay,
                north_central,
                southeastern,
                southside,
                southwest,
                west,
            ],
            [
                VACCSPReadyRegion.BLUE_RIDGE,
                VACCSPReadyRegion.CAPITAL_AREA,
                VACCSPReadyRegion.CENTRAL,
                VACCSPReadyRegion.CHESAPEAKE_BAY,
                VACCSPReadyRegion.NORTH_CENTRAL,
                VACCSPReadyRegion.SOUTHEASTERN,
                VACCSPReadyRegion.SOUTHSIDE,
                VACCSPReadyRegion.SOUTHWEST,
                VACCSPReadyRegion.WEST,
            ],
            default=VACCSPReadyRegion.CENTRAL,
        )
