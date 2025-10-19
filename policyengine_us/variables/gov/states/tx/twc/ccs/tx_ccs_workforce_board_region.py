from policyengine_us.model_api import *


class TXCCSWorkforceBoardRegion(Enum):
    PANHANDLE = "Panhandle"  # WDA 1
    SOUTH_PLAINS = "South Plains"  # WDA 2
    NORTH_TEXAS = "North Texas"  # WDA 3
    NORTH_CENTRAL = "North Central"  # WDA 4
    TARRANT_COUNTY = "Tarrant County"  # WDA 5
    DALLAS_COUNTY = "Dallas County"  # WDA 6
    NORTHEAST_TEXAS = "Northeast Texas"  # WDA 7
    EAST_TEXAS = "East Texas"  # WDA 8
    WEST_CENTRAL = "West Central"  # WDA 9
    BORDERPLEX = "Borderplex"  # WDA 10
    PERMIAN_BASIN = "Permian Basin"  # WDA 11
    CONCHO_VALLEY = "Concho Valley"  # WDA 12
    HEART_OF_TEXAS = "Heart of Texas"  # WDA 13
    CAPITAL_AREA = "Capital Area"  # WDA 14
    RURAL_CAPITAL = "Rural Capital"  # WDA 15
    BRAZOS_VALLEY = "Brazos Valley"  # WDA 16
    DEEP_EAST = "Deep East"  # WDA 17
    SOUTHEAST = "Southeast"  # WDA 18
    GOLDEN_CRESCENT = "Golden Crescent"  # WDA 19
    ALAMO = "Alamo"  # WDA 20
    SOUTH_TEXAS = "South Texas"  # WDA 21
    COASTAL_BEND = "Coastal Bend"  # WDA 22
    LOWER_RIO = "Lower Rio"  # WDA 23
    CAMERON_COUNTY = "Cameron County"  # WDA 24
    TEXOMA = "Texoma"  # WDA 25
    CENTRAL_TEXAS = "Central Texas"  # WDA 26
    MIDDLE_RIO = "Middle Rio"  # WDA 27
    GULF_COAST = "Gulf Coast"  # WDA 28


class tx_ccs_workforce_board_region(Variable):
    value_type = Enum
    possible_values = TXCCSWorkforceBoardRegion
    default_value = TXCCSWorkforceBoardRegion.PANHANDLE
    entity = Household
    definition_period = YEAR
    label = "Texas CCS workforce board region"
    defined_for = StateCode.TX
    reference = [
        "https://www.twc.texas.gov/sites/default/files/wf/docs/workforce-board-directory-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf",
    ]

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.tx.twc.ccs.region

        # Dynamically build conditions and results from enum
        conditions = []
        results = []

        for region_enum in TXCCSWorkforceBoardRegion:
            # Convert enum name to parameter name (PANHANDLE -> panhandle)
            param_name = region_enum.name.lower()
            region_param = getattr(p, param_name)

            conditions.append(np.isin(county, region_param))
            results.append(region_enum)

        return select(
            conditions,
            results,
            default=TXCCSWorkforceBoardRegion.PANHANDLE,
        )
