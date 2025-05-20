from policyengine_us.model_api import *


class is_paid_hourly(Variable):
    value_type = bool
    entity = Person
    label = "is paid hourly"
    definition_period = YEAR
