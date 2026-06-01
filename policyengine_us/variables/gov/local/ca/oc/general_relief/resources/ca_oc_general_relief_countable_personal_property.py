from policyengine_us.model_api import *


class ca_oc_general_relief_countable_personal_property(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable personal property"
    documentation = (
        "Uses available personal-property inputs. PolicyEngine does not "
        "separate all Orange County regulatory exclusions, including "
        "household effects and burial reserves."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    adds = ["personal_property"]
