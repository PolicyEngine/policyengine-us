from policyengine_us.model_api import *


class estate_tax_before_credits(Variable):
    value_type = float
    entity = Person
    label = "Estate tax before credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2001#b_1"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.tax.estate.tentative_tax_rate
        real_estate_tax = person("taxable_estate_value", period)
        return p.calc(real_estate_tax)
