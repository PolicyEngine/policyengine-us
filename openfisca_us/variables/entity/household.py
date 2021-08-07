from openfisca_core.model_api import *
from openfisca_us.entities import *


class household_id(Variable):
    value_type = float
    entity = Household
    label = u"Unique reference for this household"
    definition_period = ETERNITY


class person_household_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the household of this person"
    definition_period = ETERNITY
