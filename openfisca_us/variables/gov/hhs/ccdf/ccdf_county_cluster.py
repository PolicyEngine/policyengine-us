from openfisca_us.model_api import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = "County cluster for CCDF"
    definition_period = YEAR

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        is_unknown = county == "UNKNOWN"
        cluster_mapping = parameters(period).gov.hhs.ccdf.county_cluster
        result = np.empty_like(county)
        result[~is_unknown] = cluster_mapping[county[~is_unknown]]
        result[is_unknown] = 1
        return result
