from openfisca_us.model_api import *


class is_female(Variable):
    value_type = bool
    entity = Person
    label = "Is female"
    definition_period = YEAR

    def formula(person, period, parameters):
        sex = person("sex", period)
        return sex == sex.possible_values.FEMALE
