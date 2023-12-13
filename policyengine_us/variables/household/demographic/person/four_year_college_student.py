from policyengine_us.model_api import *


class four_year_college_student(Variable):
    value_type = bool
    entity = Person
    label = "Person is a full time four-year college student"
    definition_period = YEAR
