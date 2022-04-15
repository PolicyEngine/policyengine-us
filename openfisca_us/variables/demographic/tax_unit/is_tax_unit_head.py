from openfisca_us.model_api import *


class is_tax_unit_head(Variable):
    value_type = bool
    entity = Person
    label = "Head of tax unit"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Only adults can be heads.
        eligible = ~person("is_child", period)
        # Of those who meet the criteria, select the first person defined.
        tax_unit = person.tax_unit
        # NB: tax_unit.members_position is actually person-level.
        rank = where(eligible, tax_unit.members_position, inf)
        first_rank = tax_unit.min(rank)
        return eligible & (rank == first_rank)
