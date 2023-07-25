from policyengine_us.model_api import *


class wi_itemized_deduction_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        wi_itmded = tax_unit("itemized_deductions_less_salt", period)
        wi_stdded = tax_unit("wi_standard_deduction", period)
        excess_itmded = max_(0, wi_itmded - wi_stdded)
        p = parameters(period).gov.states.wi.tax.income
        return excess_itmded * p.credits.itemized_deduction.rate
