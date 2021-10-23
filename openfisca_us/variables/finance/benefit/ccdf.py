from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = u"County Cluster for CCDF"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        state_code = household("state_code", period).decode_to_str()
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).benefit.CCDF.county_cluster
        return cluster_mapping[state_code][county]
