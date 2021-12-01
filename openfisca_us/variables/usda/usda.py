from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class is_usda_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether person is disabled per USDA definition, see https://www.law.cornell.edu/uscode/text/7/2014"
    label = "USDA disabled status"

    def formula(person, period, parameters):
        disabled_programs = parameters(period).usda.disabled_programs

        return person("disabled_program", period)
