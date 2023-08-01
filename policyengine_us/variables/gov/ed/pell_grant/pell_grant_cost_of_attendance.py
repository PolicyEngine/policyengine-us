from policyengine_us.model_api import *


class pell_grant_cost_of_attendance(Variable):
    value_type = float
    entity = Person
    label = "Cost of Attendance"
    definition_period = YEAR
