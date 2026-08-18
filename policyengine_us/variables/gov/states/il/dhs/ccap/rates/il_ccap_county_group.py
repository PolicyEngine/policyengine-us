from policyengine_us.model_api import *


class ILCCAPCountyGroup(Enum):
    GROUP_1A = "Group 1A"
    GROUP_1B = "Group 1B"
    GROUP_2 = "Group 2"


class il_ccap_county_group(Variable):
    value_type = Enum
    entity = Household
    possible_values = ILCCAPCountyGroup
    default_value = ILCCAPCountyGroup.GROUP_2
    definition_period = MONTH
    label = "Illinois CCAP provider rate county group"
    defined_for = StateCode.IL
    reference = "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1"

    def formula(household, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.rates.county_group
        county = household("county_str", period.this_year)
        group_1a = np.isin(county, p.group_1a)
        group_1b = np.isin(county, p.group_1b)
        group_2 = ~(group_1a | group_1b)
        return select(
            [group_1a, group_1b, group_2],
            [
                ILCCAPCountyGroup.GROUP_1A,
                ILCCAPCountyGroup.GROUP_1B,
                ILCCAPCountyGroup.GROUP_2,
            ],
            default=ILCCAPCountyGroup.GROUP_2,
        )
