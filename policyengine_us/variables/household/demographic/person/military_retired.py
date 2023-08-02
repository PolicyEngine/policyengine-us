from policyengine_us.model_api import *


class military_retired(Variable):
    value_type = bool
    entity = Person
    label = "Tax unit head is retired from United State military"
    definition_period = YEAR
