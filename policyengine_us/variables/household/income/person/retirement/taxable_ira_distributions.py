from policyengine_us.model_api import *


class taxable_ira_distributions(Variable):
    value_type = float
    entity = Person
    label = "Taxable IRA distributions"
    unit = USD
    documentation = "Taxable distributions from individual retirement accounts (typically traditional IRAs)."
    definition_period = YEAR
