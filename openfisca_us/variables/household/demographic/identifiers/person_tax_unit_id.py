from openfisca_us.model_api import *


class person_tax_unit_id(Variable):
    value_type = int
    entity = Person
    label = "Unique reference for the tax unit of this person"
    definition_period = ETERNITY
