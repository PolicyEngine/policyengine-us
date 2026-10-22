from policyengine_us.model_api import *


class wi_itemized_deduction_credit_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction for Wisconsin's itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/5",
        "https://www.revenue.wi.gov/TaxForms2020/2020-Form1-inst.pdf#page=17",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=16",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        return tax_unit("charitable_deduction", period)

    def formula_2020(tax_unit, period, parameters):
        charitable = tax_unit("charitable_deduction", period)
        # The federal variable is a potential allowance, including for itemizers.
        # Only non-itemizers claim it on Form 1040 line 10b in 2020.
        claimed_above_the_line = where(
            tax_unit("tax_unit_itemizes", period),
            0,
            tax_unit("charitable_deduction_for_non_itemizers", period),
        )
        return max_(0, charitable - claimed_above_the_line)

    def formula_2021(tax_unit, period, parameters):
        return tax_unit("charitable_deduction", period)
