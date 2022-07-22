from openfisca_us.model_api import *


class social_security(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security benefits, not including SSI"
    label = "Social Security"
    unit = USD

    def formula(person, period, parameters):
        disabled_programs = parameters(period).simulation.disabled_programs
        if "social_security" in disabled_programs:
            return person("social_security_reported", period)
        SS_TYPES = ["dependents", "disability", "retirement", "survivors"]
        return add(person, period, ["social_security_" + i for i in SS_TYPES])
