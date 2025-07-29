from policyengine_us.model_api import *


class ca_riv_general_relief_special_needs(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Riverside County General Relief special needs"
    definition_period = YEAR
    defined_for = "in_riv"

    adds = ["gov.local.ca.riv.general_relief.special_needs.amount"]
