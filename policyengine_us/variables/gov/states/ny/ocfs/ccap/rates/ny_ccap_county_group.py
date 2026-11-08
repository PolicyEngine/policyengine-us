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
        "New York sets market rates by the child care provider's county. "
        "The model has no provider location, so this variable reads the "
        "household's county instead. Without a county or county FIPS input, "
        "the county variable falls back to the state's alphabetically first "
        "county, Albany County, in group 2. A county outside the four group "
        "lists, such as UNKNOWN, falls to group 3. Wherever OCFS publishes a "
        "nonzero rate in the October 2024 schedule, group 3 has the lowest "
        "rate and group 2 the next lowest. So the Albany fallback "
        "overstates rates for households in group 3 and understates them in "
        "group 1 (Nassau, Putnam, Rockland, Suffolk, Westchester) and group 4 "
        "(the five New York City boroughs)."
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
