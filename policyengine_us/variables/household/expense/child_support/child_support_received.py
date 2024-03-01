from policyengine_us.model_api import *


class child_support_received(Variable):
    value_type = float
    entity = Person
    label = "Child support receipt"
    unit = USD
    documentation = "Value of child support benefits received."
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
