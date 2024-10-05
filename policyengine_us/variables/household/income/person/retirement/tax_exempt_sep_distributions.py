from policyengine_us.model_api import *


class tax_exempt_sep_distributions(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt SEP distributions"
    unit = USD
    definition_period = YEAR
