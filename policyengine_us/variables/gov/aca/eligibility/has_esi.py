from policyengine_us.model_api import *


class has_esi(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has ESI"
    definition_period = YEAR
