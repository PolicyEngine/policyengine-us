from policyengine_us.model_api import *


class has_daca_tps_status(Variable):
    value_type = bool
    entity = Person
    label = "Has DACA or TPS immigration status"
    definition_period = YEAR
