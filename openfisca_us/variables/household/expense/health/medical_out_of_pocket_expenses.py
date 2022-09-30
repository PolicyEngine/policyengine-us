from openfisca_us.model_api import *


class medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medical out of pocket expenses"
    unit = USD
    definition_period = YEAR
    question = "How much do you spend on out of pocket medical costs?"
