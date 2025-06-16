from policyengine_us.model_api import *


class self_employment_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment Medicare tax"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1401#b_1"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.self_employment.rate
        return p.medicare * person("taxable_self_employment_income", period)
