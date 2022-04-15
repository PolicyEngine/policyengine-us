from openfisca_us.model_api import *


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Establish basic conditions.
        is_adult = person("age", period) >= 18
        is_not_head = ~person("is_tax_unit_head", period)
        eligible = is_adult * is_not_head
        # Of those who meet the criteria, select the first person defined.
        tax_unit = person.tax_unit
        # NB: tax_unit.members_position is actually person-level.
        rank = where(eligible, tax_unit.members_position, inf)
        first_rank = tax_unit.min(rank)
        return eligible & (rank == first_rank)
