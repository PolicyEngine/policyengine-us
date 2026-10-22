from policyengine_us.model_api import *


class wi_itemized_deduction_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/5",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1.pdf#page=4",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=16",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1NPR-Inst.pdf#page=34",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1.pdf#page=4",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Schedule 1 uses actual or hypothetical Schedule A components,
        # excluding SALT, miscellaneous deductions, and the federal
        # charitable allowance for non-itemizers.
        wi_itmded = add(
            tax_unit,
            period,
            [
                "medical_expense_deduction",
                "interest_deduction",
                "charitable_deduction",
                "casualty_loss_deduction",
            ],
        )
        # Exclude mortgage insurance premiums included in federal interest.
        wi_itmded -= tax_unit("deductible_mortgage_insurance_premiums", period)
        wi_stdded = tax_unit("wi_standard_deduction", period)
        excess_itmded = max_(0, wi_itmded - wi_stdded)
        p = parameters(period).gov.states.wi.tax.income
        return excess_itmded * p.credits.itemized_deduction.rate
