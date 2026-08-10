from policyengine_us.model_api import *


class receives_ssi(Variable):
    value_type = bool
    entity = Person
    label = "Reported to receive SSI"
    definition_period = MONTH
