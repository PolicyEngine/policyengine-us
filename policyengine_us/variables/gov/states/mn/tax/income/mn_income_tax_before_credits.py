from policyengine_us.model_api import *


class mn_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN
    adds = ["mn_basic_tax", "mn_amt"]
