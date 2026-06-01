from policyengine_us.model_api import *


class ca_oc_general_relief_aided_person_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "Orange County General Relief aided person count"
    definition_period = MONTH
    defined_for = "in_oc"
    adds = ["ca_oc_general_relief_eligible_person"]
