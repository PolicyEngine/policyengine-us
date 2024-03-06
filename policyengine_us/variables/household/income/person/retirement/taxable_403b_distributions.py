from policyengine_us.model_api import *


class taxable_403b_distributions(Variable):
    value_type = float
    entity = Person
    label = "Taxable 403(b) distributions"
    unit = USD
    documentation = (
        "Taxable distributions from 403b accounts (typically traditional)."
    )
    definition_period = YEAR
