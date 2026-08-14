from policyengine_us.model_api import *


class NYCCAPCountyGroup(Enum):
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"
    GROUP_3 = "Group 3"
    GROUP_4 = "Group 4"


class ny_ccap_county_group(Variable):
    value_type = Enum
    possible_values = NYCCAPCountyGroup
    default_value = NYCCAPCountyGroup.GROUP_3
    entity = Household
    label = "New York CCAP county group"
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "New York keys rates to the child care provider's county. "
        "Because provider location is not represented, this variable uses "
        "household county as a proxy and defaults unknown counties to group "
        "3. Group 3 carries the lowest rates in the current schedule, so any "
        "household whose county does not resolve is understated by 10 to 19 "
        "percent against group 2, 24 to 34 percent against group 1 (Nassau, "
        "Putnam, Rockland, Suffolk, Westchester), and 21 to 37 percent "
        "against group 4 (the five New York City boroughs). Groups 1 and 4 "
        "hold the large majority of New York's child population, so the "
        "default biases microsimulation results downward wherever county is "
        "unimputed."
    )
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=14"
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        groups = parameters(period).gov.states.ny.ocfs.ccap.county_group
        conditions = [
            np.isin(county, groups.group_1),
            np.isin(county, groups.group_2),
            np.isin(county, groups.group_3),
            np.isin(county, groups.group_4),
        ]
        values = [
            NYCCAPCountyGroup.GROUP_1,
            NYCCAPCountyGroup.GROUP_2,
            NYCCAPCountyGroup.GROUP_3,
            NYCCAPCountyGroup.GROUP_4,
        ]
        return select(
            conditions,
            values,
            default=NYCCAPCountyGroup.GROUP_3,
        )
