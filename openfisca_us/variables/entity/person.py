from openfisca_core.model_api import *
from openfisca_us.entities import *


class P_person_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for this person"
    definition_period = ETERNITY


class age(Variable):
    value_type = int
    entity = Person
    label = u"Age of the person in years"
    definition_period = YEAR
