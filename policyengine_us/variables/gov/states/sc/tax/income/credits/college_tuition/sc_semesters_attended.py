from policyengine_us.model_api import *


class sc_semesters_attended(Variable):
    value_type = float
    entity = Person
    label = "South Carolina semesters attended"
    unit = "semesters attended"
    definition_period = YEAR
    defined_for = StateCode.SC
