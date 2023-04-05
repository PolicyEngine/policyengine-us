from policyengine_us.model_api import *


class mn_marriage_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota marriage credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_22.pdf"
    )
    defined_for = StateCode.MN

    # def formula(tax_unit, period, parameters):
    #    p = parameters(period).gov.states.mn.tax.income.credits
