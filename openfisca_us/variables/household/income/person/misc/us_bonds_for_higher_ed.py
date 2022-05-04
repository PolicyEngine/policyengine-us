from openfisca_us.model_api import *


class us_bonds_for_higher_ed(Variable):
    value_type = float
    entity = Person
    label = "Income from U.S. bonds spent on higher education"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/135"
