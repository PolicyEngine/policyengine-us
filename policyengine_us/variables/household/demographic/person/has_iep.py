from policyengine_us.model_api import *


class has_iep(Variable):
    value_type = bool
    entity = Person
    label = "Has an Individualized Education Program (IEP)"
    definition_period = YEAR
