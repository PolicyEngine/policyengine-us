from openfisca_us.model_api import *


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Use order of input (first)
        return person.tax_unit.members_position == 0
