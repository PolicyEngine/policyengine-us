from openfisca_us.model_api import *


class childcare_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = u"Child care hours per week"
    definition_period = YEAR
