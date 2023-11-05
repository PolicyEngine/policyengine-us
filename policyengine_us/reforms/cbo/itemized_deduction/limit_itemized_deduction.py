from policyengine_us.model_api import *


def create_limit_itemized_deduction() -> Reform:
    class taxable_income_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ferderal taxable income deduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            standard_deduction = tax_unit("standard_deduction", period)
            p = parameters(period).gov.irs.deductions
            itemized_deductions = add(tax_unit, period, p.itemized_deductions)
            limit_percentage = parameters(
                period
            ).gov.contrib.cbo.itemized_deduction.percentage
            return max_(
                itemized_deductions * limit_percentage, standard_deduction
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income_deductions)

    return reform


def create_limit_itemized_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_limit_itemized_deduction()

    p = parameters(period).gov.contrib.cbo.itemized_deduction

    if p.percentage <= 1:
        return create_limit_itemized_deduction()
    else:
        return None


itemized_deduction = create_limit_itemized_deduction_reform(
    None, None, bypass=True
)
