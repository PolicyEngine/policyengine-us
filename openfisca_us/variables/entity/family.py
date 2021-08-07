from openfisca_core.model_api import *
from openfisca_us.entities import *


class family_id(Variable):
    value_type = float
    entity = Family
    label = u"Unique reference for this family"
    definition_period = ETERNITY


class family_weight(Variable):
    value_type = float
    entity = Family
    label = u"Family weight"
    definition_period = YEAR


class person_family_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the family of this person"
    definition_period = ETERNITY
