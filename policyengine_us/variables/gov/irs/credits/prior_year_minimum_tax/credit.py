from policyengine_us.model_api import *


class prior_year_minimum_tax_credit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Prior year minimum tax credit"
    documentation = "Prior year minimum tax credit from Form 8801"
    reference = "https://www.law.cornell.edu/uscode/text/26/53"
    unit = USD
