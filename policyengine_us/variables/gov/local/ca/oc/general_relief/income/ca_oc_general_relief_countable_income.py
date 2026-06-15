from policyengine_us.model_api import *


class ca_oc_general_relief_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable income"
    unit = USD
    definition_period = MONTH
    defined_for = "in_oc"
    adds = ["ca_oc_general_relief_countable_income_person"]
