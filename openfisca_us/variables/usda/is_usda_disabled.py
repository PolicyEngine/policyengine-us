from openfisca_us.model_api import *


class is_usda_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Disabled according to USDA criteria"
    label = "USDA disabled status"

    def formula(person, period, parameters):
        programs = parameters(period).usda.disabled_programs
        return np.any([person(program, period) for program in programs])
