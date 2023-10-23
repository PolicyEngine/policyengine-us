from policyengine_us.model_api import *


def create_limit_itemized_deduction() -> Reform:
    class itemized_deductions_less_salt(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ferderal itemized deduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.deductions
            deductions = [
                deduction
                for deduction in p.itemized_deductions
                if deduction not in ["salt_deduction"]
            ]
            # add limit percentage
            limit_percentage = parameters(
                period
            ).gov.contrib.cbo.itemized_deduction.percentage
            return add(tax_unit, period, deductions) * limit_percentage

    class reform(Reform):
        def apply(self):
            self.update_variable(itemized_deductions_less_salt)

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
