from policyengine_us.model_api import *


class mn_wfc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota working family credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1wfc_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1wfc_22_0.pdf"
    )
    defined_for = StateCode.MN

    # def formula(tax_unit, period, parameters):
    #    p = parameters(period).gov.states.mn.tax.income.credits
