from policyengine_us.model_api import *


class KSTANFCountyGroup(Enum):
    GROUP_I = "Group I (rural county)"
    GROUP_II = "Group II (high cost rural county)"
    GROUP_III = "Group III (high population county)"
    GROUP_IV = "Group IV (high cost high population county)"


class ks_tanf_county_group(Variable):
    value_type = Enum
    possible_values = KSTANFCountyGroup
    default_value = KSTANFCountyGroup.GROUP_IV
    entity = SPMUnit
    label = "Kansas TANF county group"
    definition_period = YEAR
    defined_for = StateCode.KS
    reference = "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101"

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-101: counties fall into four groups with different
        # shelter allowances. Groups I, II, and III are listed explicitly.
        # Group IV (Douglas, Harvey, Johnson, and Wyandotte — the most populous
        # counties) is the default, so any county with no listed group falls to
        # the most populous tier rather than being understated.
        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states.ks.dcf.tanf.payment_standard.county_group
        group_iii = np.isin(county, p.group_3)
        group_ii = np.isin(county, p.group_2)
        group_i = np.isin(county, p.group_1)
        return select(
            [group_iii, group_ii, group_i],
            [
                KSTANFCountyGroup.GROUP_III,
                KSTANFCountyGroup.GROUP_II,
                KSTANFCountyGroup.GROUP_I,
            ],
            default=KSTANFCountyGroup.GROUP_IV,
        )
