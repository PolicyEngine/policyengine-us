from policyengine_us.model_api import *


# sums up withheld taxes, not reported, and any uncollected taxes for social security, medicare
# also sums up additional medicare tax
class pr_federal_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico federal taxes including social security, medicare, and additional medicare tax"
    unit = USD
    definition_period = YEAR
    reference = ""
