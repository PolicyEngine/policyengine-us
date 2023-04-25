from policyengine_us.model_api import *


class mn_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_22.pdf"
    )
    defined_for = StateCode.MN
    adds = "gov.states.mn.tax.income.credits.refundable"
