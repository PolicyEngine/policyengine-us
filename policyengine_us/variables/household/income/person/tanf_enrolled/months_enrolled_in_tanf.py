from policyengine_us.model_api import *


class months_enrolled_in_tanf(Variable):
    value_type = float
    entity = Person
    label = "Months enrolled in TANF"
    definition_period = YEAR
    unit = "month"
