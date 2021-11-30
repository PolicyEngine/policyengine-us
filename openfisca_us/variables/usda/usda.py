from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class is_usda_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether person is disabled per USDA definition"
    label = ""

    def formula(persons, period, parameters):
        disabled_programs = parameters(period).usda.disabled_programs

        return where(any(persons(period).disabled_programs), True, False)
