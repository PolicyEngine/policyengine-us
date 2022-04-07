from openfisca_us.model_api import *


class self_employment_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment Medicare tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.self_employment.medicare_rate
        return rate * person("taxable_self_employment_income", period)
