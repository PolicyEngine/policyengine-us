from openfisca_core.model_api import *
from openfisca_us.entities import *


class household_id(Variable):
    value_type = float
    entity = Household
    label = u"Unique reference for this household"
    definition_period = ETERNITY


class household_weight(Variable):
    value_type = float
    entity = Household
    label = u"Household weight"
    definition_period = YEAR


class person_household_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the household of this person"
    definition_period = ETERNITY


class is_household_head(Variable):
    value_type = float
    entity = Person
    label = u"Head of household"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Use order of input (first)
        return person.household.members_position == 0
