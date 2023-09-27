from policyengine_us.model_api import *


class physician_services_expense(Variable):
    value_type = float
    entity = Person
    label = "Physician services expenses"
    unit = USD
    definition_period = YEAR
