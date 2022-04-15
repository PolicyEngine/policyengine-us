from openfisca_us.model_api import *


class is_tax_unit_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Only non-head adults can be spouses.
        adult = ~person("is_child", period)
        head = person("is_tax_unit_head", period)
        eligible = adult & ~head
        # Of those who meet the criteria, select the first person defined.
        tax_unit = person.tax_unit
        # NB: tax_unit.members_position is actually person-level.
        rank = where(eligible, tax_unit.members_position, inf)
        first_rank = tax_unit.min(rank)
        return eligible & (rank == first_rank)
