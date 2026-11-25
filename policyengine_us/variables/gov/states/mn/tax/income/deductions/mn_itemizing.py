from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class mn_itemizing(Variable):
    value_type = bool
    entity = TaxUnit
    label = "whether or not itemizing Minnesota deductions"
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
        std_ded = tax_unit("mn_standard_deduction", period)
        itm_ded = tax_unit("mn_itemized_deductions", period)
        method = tax_unit("state_deduction_method", period)
        return state_itemization_uses_itemized(method, itm_ded > std_ded)
