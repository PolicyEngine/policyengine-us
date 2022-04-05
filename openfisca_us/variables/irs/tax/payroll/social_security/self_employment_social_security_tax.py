from openfisca_us.model_api import *


class self_employment_social_security_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment Social Security tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        se = parameters(period).irs.payroll.social_security.self_employment
        return se.rate * person("txearn_sey", period)
