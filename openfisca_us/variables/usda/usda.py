from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class is_usda_elderly(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Is elderly per USDA guidelines"
    label = ""

    def formula(persons, period, parameters):
        min_age = parameters(period).usda.elderly.values.age
        return persons.members("age", period) >= min_age
