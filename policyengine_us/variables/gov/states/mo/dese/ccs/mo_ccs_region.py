from policyengine_us.model_api import *


class MOCCSRegion(Enum):
    DENSE_URBAN = "Dense urban (Region 1)"
    METRO = "Metro (Region 2)"
    URBAN = "Urban (Region 3)"
    MICROPOLITAN = "Micropolitan (Region 4)"
    RURAL = "Rural (Region 5)"


class mo_ccs_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = MOCCSRegion
    default_value = MOCCSRegion.RURAL
    definition_period = YEAR
    label = "Missouri Child Care Subsidy geographic region"
    defined_for = StateCode.MO
    reference = "https://dese.mo.gov/sites/dese/files/media/file/2025/12/2025%20Rates%20Held%20Harmless%202.0.xlsx"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.mo.dese.ccs.region
        # Region 5 (rural) is the default for any county not listed in
        # Regions 1-4.
        return select(
            [
                np.isin(county, p.region_1_counties),
                np.isin(county, p.region_2_counties),
                np.isin(county, p.region_3_counties),
                np.isin(county, p.region_4_counties),
            ],
            [
                MOCCSRegion.DENSE_URBAN,
                MOCCSRegion.METRO,
                MOCCSRegion.URBAN,
                MOCCSRegion.MICROPOLITAN,
            ],
            default=MOCCSRegion.RURAL,
        )
