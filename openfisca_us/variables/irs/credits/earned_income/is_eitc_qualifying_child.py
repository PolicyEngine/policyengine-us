from openfisca_us.model_api import *


class is_eitc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "EITC qualifying child"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/152#c"

    def formula(person, period, parameters):
        