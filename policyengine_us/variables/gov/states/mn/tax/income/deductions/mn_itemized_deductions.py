from policyengine_us.model_api import *


class mn_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota itemized deductions"
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
        # 2021 Form M1 instructions say:
        #   You may claim the Minnesota standard deduction or itemize
        #   your deductions on your Minnesota return. You will generally
        #   pay less Minnesota income tax if you take the larger of your
        #   itemized or standard deduction. 
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        us_itm_deds_less_salt = add(tax_unit, period, itm_deds)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return us_itm_deds_less_salt + uncapped_property_taxes
