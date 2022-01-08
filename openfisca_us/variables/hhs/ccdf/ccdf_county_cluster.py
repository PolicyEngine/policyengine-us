from openfisca_us.model_api import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = "County cluster for CCDF"
    definition_period = YEAR

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).hhs.ccdf.county_cluster
        return cluster_mapping[county]
