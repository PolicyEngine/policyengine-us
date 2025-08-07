from policyengine_us.model_api import *


class self_employment_social_security_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment Social Security tax"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1401#a"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.self_employment.rate
        income = person(
            "social_security_taxable_self_employment_income", period
        )
        return p.social_security * income
