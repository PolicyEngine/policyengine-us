from policyengine_us.model_api import *


class estate_tax_after_credits(Variable):
    value_type = float
    entity = Person
    label = "Estate tax after credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.estate
        deceased_eligible = person("is_deceased", period)
        base_amount = p.base * deceased_eligible

        estate_tax_before_credits = person("estate_tax_before_credits", period)
        # A deceased spouse unused exclusion amount can be computed.
        return min_(base_amount, estate_tax_before_credits)
