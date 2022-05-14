from openfisca_us.model_api import *


class medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medical out of pocket expenses"
    documentation = "Person's medical out of pocket expenses"
    unit = USD
    definition_period = YEAR
