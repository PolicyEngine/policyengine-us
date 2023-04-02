from policyengine_us.model_api import *


class mn_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota deductions"
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
        std_ded = tax_unit("mn_standard_deduction", period)
        itm_ded = tax_unit("mn_itemized_deductions", period)
        itemizing = tax_unit("mn_itemizing", period)
        return where(itemizing, itm_ded, std_ded)
