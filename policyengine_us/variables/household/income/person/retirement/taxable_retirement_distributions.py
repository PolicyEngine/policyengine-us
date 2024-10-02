from policyengine_us.model_api import *


class taxable_retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Taxable retirement account distributions"
    unit = USD
    definition_period = YEAR
    adds = [
        "taxable_ira_distributions",
        "taxable_401k_distributions",
        "taxable_sep_distributions",
        "taxable_403b_distributions",
        "keogh_distributions",
    ]
