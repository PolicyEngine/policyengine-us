from openfisca_us.model_api import *


class qualified_tuition_expenses(Variable):
    value_type = float
    entity = Person
    label = "Qualified tuition expenses"
    unit = USD
    definition_period = YEAR
