from policyengine_us.model_api import *


class pell_grant_student_assets(Variable):
    value_type = float
    entity = Person
    label = "Student Assets"
    definition_period = YEAR
