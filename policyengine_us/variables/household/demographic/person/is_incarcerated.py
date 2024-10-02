from policyengine_us.model_api import *


class is_incarcerated(Variable):
    value_type = bool
    entity = Person
    label = "Is incarcerated"
    documentation = "Whether this person is incarcerated."
    definition_period = MONTH
