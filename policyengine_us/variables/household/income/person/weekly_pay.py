from policyengine_us.model_api import *


class weekly_pay(Variable):
    value_type = float
    entity = Person
    label = (
        "Usually earned weekly pay before deductions (subject to topcoding)"
    )
    unit = USD
    definition_period = YEAR
