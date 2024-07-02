from policyengine_us.model_api import *


class taxable_estate_value(Variable):
    value_type = float
    entity = Person
    label = "Taxable estate value"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2001#b_1"
