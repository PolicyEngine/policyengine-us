from policyengine_us.model_api import *


class ma_tafdc_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) unearned income"
    definition_period = YEAR
    reference = (
        "https://www.masslegalservices.org/content/62-what-income-counted"
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income
        total_unearned_income = add(tax_unit, period, p.unearned)
        child_support_deduction = add(
            tax_unit, period, ["ma_tafdc_child_support_deduction"]
        )
        return max_(0, total_unearned_income - child_support_deduction)
