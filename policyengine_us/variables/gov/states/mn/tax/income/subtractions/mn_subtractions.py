from policyengine_us.model_api import *


class mn_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_21_0.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_inst_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_22.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2024-02/m1-inst-22.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.subtractions
        total_subtractions = add(tax_unit, period, p.sources)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
