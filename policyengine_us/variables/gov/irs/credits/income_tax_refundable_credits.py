from policyengine_us.model_api import *


class income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "federal refundable income tax credits"
    unit = USD
    adds = "gov.irs.credits.refundable"
