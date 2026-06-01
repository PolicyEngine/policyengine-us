from policyengine_us.model_api import *


class ca_oc_general_relief_home_equity(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief home equity"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    adds = ["home_equity"]
