from openfisca_core.model_api import *
from openfisca_us.entities import *


class person_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for this person"
    definition_period = ETERNITY


class person_weight(Variable):
    value_type = float
    entity = Person
    label = u"Person weight"
    definition_period = YEAR


class age(Variable):
    value_type = int
    entity = Person
    label = u"Age"
    definition_period = YEAR
