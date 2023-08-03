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
        # ... calculate pre-limitation itemized deductions
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        mn_itm_deds = itm_deds_less_salt + capped_property_taxes
        # ... calculate itemized deductions offset
        p = parameters(period).gov.states.mn.tax.income.deductions
        exempt_deds = add(
            tax_unit,
            period,
            ["medical_expense_deduction", "casualty_loss_deduction"],
        )
        net_deds = max_(0, mn_itm_deds - exempt_deds)
        net_deds_offset = p.deduction_fraction * net_deds
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        excess_agi_offset = p.excess_agi_fraction * excess_agi
        offset = min_(net_deds_offset, excess_agi_offset)
        return max_(0, mn_itm_deds - offset)
