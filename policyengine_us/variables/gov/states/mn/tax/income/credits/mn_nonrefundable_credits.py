from policyengine_us.model_api import *


class mn_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota nonrefundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1c_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1c_22.pdf"
    )
    defined_for = StateCode.MN
    adds = "gov.states.mn.tax.income.credits.nonrefundable"
