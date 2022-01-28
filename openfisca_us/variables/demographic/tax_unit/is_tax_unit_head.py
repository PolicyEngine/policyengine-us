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
        rank = person.tax_unit.members_position * eligible
        highest_rank = person.tax_unit.sum(rank)
        return eligible & (rank == highest_rank)
