from policyengine_us.model_api import *


class pr_refundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico refundable credit"
    unit = USD 
    definition_period = YEAR
    defined_for = StateCode.PR

    adds = "gov.territories.pr.tax.income.credits.refundable"
