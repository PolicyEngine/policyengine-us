from openfisca_us.model_api import *


class social_security(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security benefits, not including SSI"
    label = "Social Security"
    unit = USD

    def formula(person, period, parameters):
        SS_TYPES = ["dependents", "disability", "retirement", "survivors"]
        return add(person, period, ["social_security_" + i for i in SS_TYPES])
