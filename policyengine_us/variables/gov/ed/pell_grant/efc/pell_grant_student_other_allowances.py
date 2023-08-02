from policyengine_us.model_api import *


class pell_grant_student_other_allowances(Variable):
    value_type = float
    entity = Person
    label = "Student Other Allowances"
    definition_period = YEAR
