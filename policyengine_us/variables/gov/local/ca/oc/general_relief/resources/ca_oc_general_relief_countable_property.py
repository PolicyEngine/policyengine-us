from policyengine_us.model_api import *


class ca_oc_general_relief_countable_property(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable property"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    adds = [
        "ca_oc_general_relief_countable_personal_property",
        "ca_oc_general_relief_other_real_estate_equity",
        "ca_oc_general_relief_countable_vehicle_value",
    ]
