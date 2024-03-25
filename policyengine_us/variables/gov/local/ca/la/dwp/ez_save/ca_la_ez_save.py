from policyengine_us.model_api import *


class ca_la_ez_save(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Los Angeles County EZ Save program"
    defined_for = "ca_la_ez_save_eligible"

    adds = ["ca_la_ez_save_amount"]