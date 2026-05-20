from policyengine_us.model_api import *


class VACCSPLocalityGroup(Enum):
    GROUP_I = "Group I"
    GROUP_II = "Group II"
    GROUP_III = "Group III"


class va_ccsp_locality_group(Variable):
    value_type = Enum
    possible_values = VACCSPLocalityGroup
    default_value = VACCSPLocalityGroup.GROUP_I
    entity = SPMUnit
    label = "Virginia CCSP locality group"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section40/",
        "https://www.childcare.virginia.gov/home/showpublisheddocument/66667/638981099706730000#page=204",
    )

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states.va.dss.ccsp.localities

        group3 = np.isin(county, p.group3)
        group2 = np.isin(county, p.group2)

        return select(
            [group3, group2],
            [
                VACCSPLocalityGroup.GROUP_III,
                VACCSPLocalityGroup.GROUP_II,
            ],
            default=VACCSPLocalityGroup.GROUP_I,
        )
