from policyengine_us.model_api import *


class GACAPSZone(Enum):
    ZONE_1 = "Zone 1"
    ZONE_2 = "Zone 2"
    ZONE_3 = "Zone 3"


class ga_caps_zone(Variable):
    value_type = Enum
    entity = Household
    possible_values = GACAPSZone
    default_value = GACAPSZone.ZONE_3
    definition_period = MONTH
    defined_for = StateCode.GA
    label = "Georgia CAPS geographic zone"
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixC-CAPS%20Reimbursement%20Rates.pdf#page=2"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.ga.decal.caps
        is_zone_1 = np.isin(county, p.zone_1_counties)
        is_zone_2 = np.isin(county, p.zone_2_counties)
        is_zone_3 = np.isin(county, p.zone_3_counties)
        return select(
            [is_zone_1, is_zone_2, is_zone_3],
            [GACAPSZone.ZONE_1, GACAPSZone.ZONE_2, GACAPSZone.ZONE_3],
            default=GACAPSZone.ZONE_3,
        )
