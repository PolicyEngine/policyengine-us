from policyengine_us.model_api import *


class pell_grant_students_in_college(Variable):
    value_type = float
    entity = Person
    label = "Students in College"
    definition_period = YEAR
