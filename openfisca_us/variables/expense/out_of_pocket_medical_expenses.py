from openfisca_us.model_api import *


class out_of_pocket_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Out of pocket medical expenses"
    documentation = "Person's out of pocket medical expenses"
    unit = USD
    definition_period = YEAR
