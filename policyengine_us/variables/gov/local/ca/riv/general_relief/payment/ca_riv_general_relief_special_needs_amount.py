from policyengine_us.model_api import *


class ca_riv_general_relief_special_needs_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief special needs amount"
    definition_period = YEAR
    defined_for = "in_riv"

    adds = [
        "gov.local.ca.riv.general_relief.needs_standards.special_needs.transportation"
    ]
