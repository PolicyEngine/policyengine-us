from openfisca_us.model_api import *


class has_telephone_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has telephone costs"
    documentation = "Whether the household has telephone (or equivalent) costs"
    definition_period = YEAR
