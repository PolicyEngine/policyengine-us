from policyengine_us.model_api import *


class NYCCAPCountyGroup(Enum):
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"
    GROUP_3 = "Group 3"
    GROUP_4 = "Group 4"
    GROUP_5 = "Group 5"


class ny_ccap_county_group(Variable):
    value_type = Enum
    possible_values = NYCCAPCountyGroup
    default_value = NYCCAPCountyGroup.GROUP_3
    entity = Household
    label = "New York CCAP county group"
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "New York keys rates to the child care provider's county. "
        "Because provider location is not represented, this variable uses "
        "household county as a proxy and defaults unknown counties to group 3."
    )
    reference = (
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=14"
    )

    def formula(household, period, parameters):
        county = household("county_str", period.this_year)
        p = parameters(period).gov.states.ny.ocfs.ccap
        if p.current_rates_in_effect:
            groups = p.current_county_group
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

        historical = p.historical_county_group
        county_names = list(historical._children)
        group_values = np.array(
            [historical[county_name] for county_name in county_names]
        )
        county_names = np.array(county_names)
        conditions = [
            np.isin(county, county_names[group_values == group])
            for group in range(1, 6)
        ]
        return select(
            conditions,
            [
                NYCCAPCountyGroup.GROUP_1,
                NYCCAPCountyGroup.GROUP_2,
                NYCCAPCountyGroup.GROUP_3,
                NYCCAPCountyGroup.GROUP_4,
                NYCCAPCountyGroup.GROUP_5,
            ],
            default=NYCCAPCountyGroup.GROUP_3,
        )
