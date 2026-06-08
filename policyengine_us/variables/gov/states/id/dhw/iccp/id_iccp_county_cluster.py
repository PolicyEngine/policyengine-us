from policyengine_us.model_api import *


class IDICCPCountyCluster(Enum):
    CLUSTER_1 = "Cluster 1"
    CLUSTER_2 = "Cluster 2"
    CLUSTER_3 = "Cluster 3"


class id_iccp_county_cluster(Variable):
    value_type = Enum
    entity = Household
    possible_values = IDICCPCountyCluster
    default_value = IDICCPCountyCluster.CLUSTER_1
    definition_period = YEAR
    label = "Idaho Child Care Program county cluster"
    defined_for = StateCode.ID
    reference = "https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.id.dhw.iccp.county_cluster
        return select(
            [
                np.isin(county, p.cluster_3),
                np.isin(county, p.cluster_2),
            ],
            [
                IDICCPCountyCluster.CLUSTER_3,
                IDICCPCountyCluster.CLUSTER_2,
            ],
            default=IDICCPCountyCluster.CLUSTER_1,
        )
