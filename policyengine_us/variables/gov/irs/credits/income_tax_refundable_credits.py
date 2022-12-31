from policyengine_us.model_api import *


class income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "federal refundable tax credits"
    unit = USD

    formula = sum_of_variables("gov.irs.credits.refundable")
    # formula must use a parameter list that varies by period
