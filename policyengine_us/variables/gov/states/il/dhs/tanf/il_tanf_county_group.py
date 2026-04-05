from policyengine_us.model_api import *


class ILTANFCountyGroup(Enum):
    GROUP_I = "Group I"
    GROUP_II = "Group II"
    GROUP_III = "Group III"


class il_tanf_county_group(Variable):
    value_type = Enum
    possible_values = ILTANFCountyGroup
    default_value = ILTANFCountyGroup.GROUP_II
    entity = SPMUnit
    label = "Illinois TANF county group for regional payment levels"
    definition_period = MONTH
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500830403chi"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)

        p = parameters(period).gov.states.il.dhs.tanf.county_group
        is_group_i = np.isin(county, p.group_i)
        is_group_iii = np.isin(county, p.group_iii)

        return select(
            [is_group_i, is_group_iii],
            [
                ILTANFCountyGroup.GROUP_I,
                ILTANFCountyGroup.GROUP_III,
            ],
            default=ILTANFCountyGroup.GROUP_II,
        )
