from policyengine_us.model_api import *


class estate_tax(Variable):
    value_type = float
    entity = Person
    label = "Estate tax"
    unit = USD
    definition_period = YEAR
    defined_for = "is_deceased"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2001#b",
        "https://www.law.cornell.edu/uscode/text/26/2010#d",
    )

    def formula(person, period, parameters):
        estate_tax_before_credits = person("estate_tax_before_credits", period)
        estate_tax_credit = person("estate_tax_credit", period)
        # 26 U.S.C. 2010(d): the credit cannot exceed the tax.
        return max_(0, estate_tax_before_credits - estate_tax_credit)
