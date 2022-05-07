from openfisca_us.model_api import *


class student_loan_interest(Variable):
    value_type = float
    entity = Person
    label = "Student loan interest expense"
    unit = USD
    definition_period = YEAR
