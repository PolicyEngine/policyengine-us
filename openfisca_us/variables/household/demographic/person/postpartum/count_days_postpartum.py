from openfisca_us.model_api import *


class count_days_postpartum(Variable):
    value_type = int
    entity = Person
    label = "Number of days postpartum"
    unit = "day"
    definition_period = YEAR
