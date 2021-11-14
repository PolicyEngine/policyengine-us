from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *


class ccdf_county_cluster(Variable):
    value_type = int
    entity = Household
    label = u"County cluster for CCDF"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()
        cluster_mapping = parameters(period).benefit.ccdf.county_cluster
        return cluster_mapping[county]


class ccdf_market_rate(Variable):
    value_type = float
    entity = Person
    label = u"CCDF market rate"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        county_cluster = person("ccdf_county_cluster", period)
        provider_type_group = person("provider_type_group", period)
        child_age_group = person("ccdf_age_group", period)
        duration_of_care = person("duration_of_care", period)
        market_rate_mapping = parameters(period).benefit.ccdf.amount
        return market_rate_mapping[county_cluster][provider_type_group][
            child_age_group
        ][duration_of_care]
