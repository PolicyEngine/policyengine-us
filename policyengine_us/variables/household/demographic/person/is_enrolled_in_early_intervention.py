from policyengine_us.model_api import *


class is_enrolled_in_early_intervention(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in Part C Early Intervention services"
    definition_period = YEAR
