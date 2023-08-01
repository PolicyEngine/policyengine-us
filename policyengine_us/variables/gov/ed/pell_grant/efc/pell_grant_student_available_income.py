from policyengine_us.model_api import *


class pell_grant_student_available_income(Variable):
    value_type = float
    entity = Person
    label = "Student Availble Income"
    definition_period = YEAR
