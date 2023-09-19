from policyengine_us.model_api import *


class receives_railroad_benefits(Variable):
    value_type = bool
    entity = Person
    label = "Recieves any railroad benefits"
    definition_period = YEAR
    default_value = False
