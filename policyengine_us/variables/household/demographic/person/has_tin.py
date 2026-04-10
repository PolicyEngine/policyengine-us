from policyengine_us.model_api import *


class has_tin(Variable):
    value_type = bool
    entity = Person
    label = "Has TIN (ITIN or SSN)"
    definition_period = YEAR
    default_value = True

    def formula(person, period, parameters):
        # Temporary migration shim: legacy inputs still set `has_itin`.
        return person("has_itin", period)
