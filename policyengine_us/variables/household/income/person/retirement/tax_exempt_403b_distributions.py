from policyengine_us.model_api import *


class tax_exempt_403b_distributions(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt 403(b) distributions"
    unit = USD
    documentation = (
        "Tax-exempt distributions from 403(b) accounts (typically Roth)."
    )
    definition_period = YEAR
