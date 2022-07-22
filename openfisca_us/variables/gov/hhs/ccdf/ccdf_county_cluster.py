from openfisca_us.model_api import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = "County cluster for CCDF"
    definition_period = YEAR

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).gov.hhs.ccdf.county_cluster
        result = np.ones_like(county, dtype=int)
        valid_county = np.isin(
            county, np.array(list(cluster_mapping._children))
        )
        if valid_county.sum() > 0:
            result[valid_county] = cluster_mapping[county[valid_county]]
        return result
