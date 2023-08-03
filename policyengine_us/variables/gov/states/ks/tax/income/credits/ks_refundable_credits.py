from policyengine_us.model_api import *


class ks_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS
    adds = "gov.states.ks.tax.income.credits.refundable"
