from policyengine_us.model_api import *


class current_pregnancy_month(Variable):
    value_type = int
    entity = Person
    label = "Current pregnancy month"
    definition_period = MONTH
    defined_for = "is_pregnant"
    default_value = 9
