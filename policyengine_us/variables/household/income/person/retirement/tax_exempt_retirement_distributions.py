from policyengine_us.model_api import *


class tax_exempt_retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt retirement account distributions"
    unit = USD
    definition_period = YEAR
    adds = [
        "tax_exempt_ira_distributions",
        "tax_exempt_401k_distributions",
        "tax_exempt_sep_distributions",
        "tax_exempt_403b_distributions",
    ]
