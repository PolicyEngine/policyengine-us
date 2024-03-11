from policyengine_us.model_api import *


class keogh_distributions(Variable):
    value_type = float
    entity = Person
    label = "KEOGH distributions"
    unit = USD
    definition_period = YEAR


taxable_ira_distributions
    - taxable_401k_distributions
    - taxable_sep_distributions
    - taxable_403b_distributions
    - keogh_distributions # Keogh plans don't have a Roth option.