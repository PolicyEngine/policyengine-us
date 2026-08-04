from policyengine_us.model_api import *


class id_iccp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program family copay"
    defined_for = StateCode.ID
    adds = ["id_iccp_copay_per_child"]
