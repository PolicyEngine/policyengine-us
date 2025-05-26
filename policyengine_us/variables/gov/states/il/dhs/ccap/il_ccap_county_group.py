from policyengine_us.model_api import *


class IllinoisCCAPCountyGroup(Enum):
    COUNTY_1A = "County 1A"
    COUNTY_1B = "County 1B"
    COUNTY_2 = "County 2"


class il_ccap_county_group(Variable):
    value_type = Enum
    entity = Household
    possible_values = IllinoisCCAPCountyGroup
    default_value = IllinoisCCAPCountyGroup.COUNTY_1A
    definition_period = MONTH
    defined_for = StateCode.IL
    label = "Illinois Child Care Assistance Program (CCAP) county group"
    reference = "https://www.dhs.state.il.us/page.aspx?item=163817"

    # def formula(household, period, parameters):
    #     county = household("county_str", period)

    #     p = parameters(period).gov.states.il.dhs.ccap.county_group
    #     county_1a = np.isin(county, p.county_1a)
    #     county_1b = np.isin(county, p.county_1b)
    #     county_2 = np.isin(county, p.county_2)

    #     conditions = [
    #         county_1a,
    #         county_1b,
    #         county_2,
    #     ]
    #     results = [
    #         IllinoisCCAPCountyGroup.COUNTY_1A,
    #         IllinoisCCAPCountyGroup.COUNTY_1B,
    #         IllinoisCCAPCountyGroup.COUNTY_2,
    #     ]

    #     return select(
    #         conditions,
    #         results,
    #         default=IllinoisCCAPCountyGroup.COUNTY_1A,
    #     )
