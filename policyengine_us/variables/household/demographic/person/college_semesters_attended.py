from policyengine_us.model_api import *


class college_semesters_attended(Variable):
    value_type = int
    entity = Person
    label = "College semesters attended"
    unit = "semesters attended"
    definition_period = YEAR
