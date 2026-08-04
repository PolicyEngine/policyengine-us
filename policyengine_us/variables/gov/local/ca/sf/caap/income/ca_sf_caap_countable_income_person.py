from policyengine_us.model_api import *


class ca_sf_caap_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "San Francisco County CAAP countable income per person"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    adds = [
        "ca_sf_caap_net_earned_income",
        "ca_sf_caap_unearned_income",
    ]
