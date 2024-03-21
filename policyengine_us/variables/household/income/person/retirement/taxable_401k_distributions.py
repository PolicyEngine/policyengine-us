from policyengine_us.model_api import *


class taxable_401k_distributions(Variable):
    value_type = float
    entity = Person
    label = "Taxable 401(k) distributions"
    unit = USD
    documentation = (
        "Taxable distributions from 401k accounts (typically traditional)."
    )
    definition_period = YEAR
