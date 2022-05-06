from openfisca_us.model_api import *


class under_60_days_postpartum(Variable):
    value_type = bool
    entity = Person
    label = "Under 60 days postpartum"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        count_days_postpartum = person("count_days_postpartum", period)
        return count_days_postpartum < 60
