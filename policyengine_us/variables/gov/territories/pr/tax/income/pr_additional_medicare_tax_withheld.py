from policyengine_us.model_api import *


class pr_additional_medicare_tax_withheld(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico additional medicare tax withheld"
    unit = USD
    definition_period = YEAR
    reference = ""
