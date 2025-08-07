from policyengine_us.model_api import *


class pr_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    adds = "gov.territories.pr.tax.income.credits.refundable"
