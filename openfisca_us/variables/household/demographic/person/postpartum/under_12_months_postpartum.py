from openfisca_us.model_api import *


class under_12_months_postpartum(Variable):
    value_type = bool
    entity = Person
    label = "Under 12 months postpartum"
    definition_period = YEAR

    def formula(person, period, parameters):
        count_days_postpartum = person("count_days_postpartum", period)
        return count_days_postpartum < 365
