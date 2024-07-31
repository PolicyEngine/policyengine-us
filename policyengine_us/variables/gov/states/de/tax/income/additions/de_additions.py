from policyengine_us.model_api import *


class de_additions(Variable):
    value_type = float
    entity = Person
    label = "Delaware adjusted gross income additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
