from policyengine_us.model_api import *


class ca_sf_caap_net_earned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "San Francisco County CAAP net earned income after disregard"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        earned = person("ca_sf_caap_earned_income", period)
        disregard = person("ca_sf_caap_earned_income_disregard", period)
        return max_(earned - disregard, 0)
