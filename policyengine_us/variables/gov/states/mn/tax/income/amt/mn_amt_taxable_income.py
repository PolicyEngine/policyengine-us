from policyengine_us.model_api import *


class mn_amt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota alternative minimum tax (AMT) taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1mt_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1mt_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        fagi = tax_unit("adjusted_gross_income", period)
        itemizing = tax_unit("mn_itemizing", period)
        SOME_DEDUCTIONS = [
            "charitable_deduction",
            "medical_expense_deduction",
            "casualty_loss_deduction",
        ]
        some_itm_deds = itemizing * add(tax_unit, period, SOME_DEDUCTIONS)
        AMT_SUBTRACTIONS = [
            "us_govt_interest",
            "mn_charity_subtraction",
            "mn_social_security_subtraction",
        ]
        amt_subs = add(tax_unit, period, AMT_SUBTRACTIONS)
        return fagi - some_itm_deds - amt_subs
