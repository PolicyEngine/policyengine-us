from openfisca_us.model_api import *


class childcare_hours_per_day(Variable):
    value_type = float
    entity = Person
    label = "Child care hours per day"
    definition_period = YEAR
    unit = "hour"
