from openfisca_us.model_api import *


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Establish basic conditions
        is_adult = person("age", period) >= 18
        is_not_head = ~person("is_tax_unit_head", period)
        eligible = is_adult * is_not_head
        # Of those who meet the criteria, select the first person defined
        rank = person.tax_unit.members_position * eligible
        highest_rank = person.tax_unit.sum(rank)
        return eligible & (rank == highest_rank)
