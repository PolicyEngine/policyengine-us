from policyengine_us.model_api import *


class military_service_income(Variable):
    value_type = float
    entity = Person
    label = "Military service income"
    unit = USD
    documentation = "Military pay from active duty, National Guard, and/or the reserve component of the armed forces."
    definition_period = YEAR
