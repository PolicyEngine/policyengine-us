from policyengine_us.model_api import *


class KSCCAPRateGroup(Enum):
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"
    GROUP_3 = "Group 3"


class ks_ccap_rate_group(Variable):
    value_type = Enum
    possible_values = KSCCAPRateGroup
    default_value = KSCCAPRateGroup.GROUP_3
    entity = Household
    label = "Kansas CCAP provider rate group"
    definition_period = YEAR
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.ks.dcf.ccap.rate_group
        # defined_for filters output but does not short-circuit execution, so
        # mask on Kansas before matching county strings; non-Kansas county
        # values would otherwise never match and silently fall to Group 3.
        in_kansas = household("state_code_str", period) == "KS"
        group_1 = in_kansas & np.isin(county, p.group_1)
        group_2 = in_kansas & np.isin(county, p.group_2)
        return select(
            [group_1, group_2],
            [
                KSCCAPRateGroup.GROUP_1,
                KSCCAPRateGroup.GROUP_2,
            ],
            default=KSCCAPRateGroup.GROUP_3,
        )
