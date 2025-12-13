from policyengine_us.model_api import *


class PATANFCountyGroup(Enum):
    GROUP_1 = "Group 1"
    GROUP_2 = "Group 2"
    GROUP_3 = "Group 3"
    GROUP_4 = "Group 4"


class pa_tanf_county_group(Variable):
    value_type = Enum
    possible_values = PATANFCountyGroup
    default_value = PATANFCountyGroup.GROUP_2
    entity = Household
    definition_period = YEAR
    label = "Pennsylvania TANF county group"
    defined_for = StateCode.PA
    reference = "http://services.dpw.state.pa.us/oimpolicymanuals/cash/168_Determining_Eligibility_and_Payment_Amount/168_Appendix_B.htm"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.pa.dhs.tanf.county_group

        group_1 = np.isin(county, p.group_1)
        group_2 = np.isin(county, p.group_2)
        group_3 = np.isin(county, p.group_3)
        group_4 = np.isin(county, p.group_4)

        conditions = [group_1, group_2, group_3, group_4]
        results = [
            PATANFCountyGroup.GROUP_1,
            PATANFCountyGroup.GROUP_2,
            PATANFCountyGroup.GROUP_3,
            PATANFCountyGroup.GROUP_4,
        ]

        return select(conditions, results, default=PATANFCountyGroup.GROUP_2)
