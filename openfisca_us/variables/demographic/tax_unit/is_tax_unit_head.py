from openfisca_us.model_api import *


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Establish basic conditions
        eligible = person("age", period) >= 18

        # Of those who meet the criteria, select the first person defined
        tax_unit = person.tax_unit
        rank = where(eligible, tax_unit.members_position, inf)
        first_rank = tax_unit.min(rank)
        return eligible & (rank == first_rank)
