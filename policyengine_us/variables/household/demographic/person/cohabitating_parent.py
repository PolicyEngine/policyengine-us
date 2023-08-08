from policyengine_us.model_api import *


class cohabitating_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Cohabitating parents"
    documentation = "Whether a parent is cohabitating with the taxfiler."

    def formula(person, period, parameters):
        return person("is_parent", period)
