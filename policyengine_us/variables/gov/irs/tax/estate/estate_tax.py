from policyengine_us.model_api import *


class estate_tax(Variable):
    value_type = float
    entity = Person
    label = "Estate tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2001#b_1"

    def formula(person, period, parameters):
        estate_tax_before_credits = person("estate_tax_before_credits", period)
        estate_tax_credit = person("estate_tax_credit", period)
        return max_(0, estate_tax_before_credits - estate_tax_credit)
