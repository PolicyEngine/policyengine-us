from policyengine_us.model_api import *


class ca_riv_general_relief_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Person's countable income before proration"
    definition_period = MONTH

    adds = [
        "ca_riv_general_relief_net_earned_income",
        "ca_riv_general_relief_unearned_income",
    ]
