from policyengine_us.model_api import *


def limit_itemized_deduction_reform() -> Reform:
    class ferderal_itemized_deduction(Variable):
        value_type = float
        entity = Person
        label = "Ferderal itemzied deduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p_us = parameters(period).gov.irs.deductions
            itm_deds = [
                deduction
                for deduction in p_us.itemized_deductions
                if deduction not in ["salt_deduction"]
            ]
            us_itemizing = tax_unit("tax_unit_itemizes", period)
            limit_percentage = parameters(
                period
            ).gov.contrib.cbo.itemized_deduction.limit_itemized_deduction
            return (
                add(tax_unit, period, itm_deds) * us_itemizing * limit_percentage
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(federal_itemized_deduction)

    return reform


def limit_itemized_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return limit_itemized_deduction_reform()

    p = parameters(period).gov.contrib.cbo.itemized_deduction

    if p.limit_itemized_deduction > 1:
        return limit_itemized_deduction_reform()
    else:
        return None


itemized_deduction = limit_itemized_deduction_reform(
    None, None, bypass=True
)