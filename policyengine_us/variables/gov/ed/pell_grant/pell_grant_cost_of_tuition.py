from policyengine_us.model_api import *


class cost_of_tuition(Variable):
    value_type = float
    entity = Person
    label = "Cost of Attendance"
    definition_period = YEAR
