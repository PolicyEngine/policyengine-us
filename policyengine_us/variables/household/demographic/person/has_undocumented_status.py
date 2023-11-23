from policyengine_us.model_api import *


class has_undocumented_status(Variable):
    value_type = bool
    entity = Person
    label = "Has undocumented immigration status"
    definition_period = YEAR
