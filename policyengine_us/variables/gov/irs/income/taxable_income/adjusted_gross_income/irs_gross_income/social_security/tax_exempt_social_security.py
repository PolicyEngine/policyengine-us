from policyengine_us.model_api import *


class tax_exempt_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax-exempt Social Security"
    unit = USD
    definition_period = YEAR

    adds = ["tax_unit_social_security"]
    subtracts = ["tax_unit_taxable_social_security"]
