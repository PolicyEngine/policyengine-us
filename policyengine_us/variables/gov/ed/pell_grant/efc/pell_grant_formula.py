from policyengine_us.model_api import *


class PellGrantFormula(Enum):
    A = "A"
    B = "B"
    C = "C"


class pell_grant_formula(Variable):
    value_type = Enum
    possible_values = PellGrantFormula
    default_value = PellGrantFormula.A
    entity = Person
    label = "Formula"
    definition_period = YEAR
