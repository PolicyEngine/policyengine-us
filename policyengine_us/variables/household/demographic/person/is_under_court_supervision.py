from policyengine_us.model_api import *


class is_under_court_supervision(Variable):
    value_type = bool
    entity = Person
    label = "Is under court supervision"
    documentation = "Whether this person is under court supervision."
    definition_period = YEAR
