from policyengine_us.model_api import *


class estate_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "Estate tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"
    defined_for = "is_deceased"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.estate
        # A deceased spouse unused exclusion amount can be computed.
        return p.base
