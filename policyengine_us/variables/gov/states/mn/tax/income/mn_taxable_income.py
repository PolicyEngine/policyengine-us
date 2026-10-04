from policyengine_us.model_api import *


class mn_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota taxable income"
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
        us_agi = tax_unit("adjusted_gross_income", period)
        adds = tax_unit("mn_additions", period)
        deductions = tax_unit("mn_deductions", period)
        exemptions = tax_unit("mn_exemptions", period)
        subs = tax_unit("mn_subtractions", period)
        return max_(0, us_agi + adds - deductions - exemptions - subs)
