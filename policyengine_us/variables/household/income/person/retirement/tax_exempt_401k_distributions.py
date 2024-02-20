from policyengine_us.model_api import *


class tax_exempt_401k_distributions(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt 401(k) distributions"
    unit = USD
    documentation = (
        "Tax-exempt distributions from 401(k) accounts (typically Roth)."
    )
    definition_period = YEAR
