from policyengine_us.model_api import *


class ca_oc_general_relief_countable_personal_property(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable personal property"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    # NOTE: uses available personal-property inputs; we don't separate all
    # Orange County exclusions (household effects up to $500, burial reserves
    # up to $1,000) at the moment.
    adds = ["personal_property"]
