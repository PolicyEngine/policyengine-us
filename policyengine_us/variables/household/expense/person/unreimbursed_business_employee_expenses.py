from policyengine_us.model_api import *


class unreimbursed_business_employee_expenses(Variable):
    value_type = float
    entity = Person
    label = "Unreimbursed business employee expenses"
    unit = USD
    definition_period = YEAR
