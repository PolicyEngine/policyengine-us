from policyengine_us.model_api import *


class mn_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        num_exemptions = tax_unit("mn_exemptions_count", period)
        p = parameters(period).gov.states.mn.tax.income.exemptions
        return num_exemptions * p.amount
