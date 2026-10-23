from policyengine_us.model_api import *


class wi_itemized_deduction_credit_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction for Wisconsin's itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/5",
        # PDF pages 2, 17
        "https://www.revenue.wi.gov/TaxForms2020/2020-Form1-inst.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=16",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        return tax_unit("charitable_deduction", period)

    def formula_2020(tax_unit, period, parameters):
        charitable = tax_unit("charitable_deduction", period)
        # Gifts claimed on federal Form 1040 line 10b; zero for itemizers.
        claimed_above_the_line = tax_unit("charitable_contributions_ald", period)
        return max_(0, charitable - claimed_above_the_line)

    def formula_2021(tax_unit, period, parameters):
        return tax_unit("charitable_deduction", period)
