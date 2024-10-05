from policyengine_us.model_api import *


class income_tax_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "federal non-refundable income tax credits"
    unit = USD
    adds = "gov.irs.credits.non_refundable"
