from policyengine_us.model_api import *


class technical_institution_student(Variable):
    value_type = bool
    entity = Person
    label = "Is a technical institution student"
    definition_period = YEAR
