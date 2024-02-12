from policyengine_us.model_api import *


class tax_exempt_ira_distributions(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt IRA distributions"
    unit = USD
    documentation = "Tax-exempt distributions from individual retirement accounts (qualifying Roth distributions)."
    definition_period = YEAR
