from policyengine_us.model_api import *


class cohabitating_grandparent(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Cohabitating grandparent"
    documentation = "Whether a grandparent is cohabitating with the taxfiler."

    def formula(person, period, parameters):
        return person("is_grandparent", period)
