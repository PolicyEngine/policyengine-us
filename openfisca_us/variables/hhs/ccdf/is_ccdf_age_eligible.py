from openfisca_us.model_api import *


class is_ccdf_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Age eligibility for CCDF"

    def formula(person, period, parameters):
        age = person("age", period)
        age_limit = parameters(period).hhs.ccdf.age_limit
        return age < age_limit
