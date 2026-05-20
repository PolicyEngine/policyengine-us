from policyengine_us.model_api import *


class taxable_roth_conversions(Variable):
    value_type = float
    entity = Person
    label = "Taxable Roth conversions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Taxable amounts converted from tax-deferred retirement accounts into "
        "Roth accounts. These amounts count in tax gross income but do not "
        "represent cash retirement distributions available for spending."
    )
