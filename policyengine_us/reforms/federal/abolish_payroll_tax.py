from policyengine_us.model_api import *
from policyengine_core.periods import period as period_

def create_abolish_payroll_tax() -> Reform:
    class household_tax_before_refundable_credits(Variable):
        value_type = float
        entity = Household
        label = "total tax before refundable credits"
        documentation = "Total tax liability before refundable credits."
        unit = USD
        definition_period = YEAR

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = (
                p.gov.household.household_tax_before_refundable_credits
            )
            added_components = [
                c for c in added_components if c != "employee_payroll_tax"
            ]
            return add(household, period, added_components)

    class reform(Reform):
        def apply(self):
            self.update_variable(household_tax_before_refundable_credits)

    return reform


def create_abolish_payroll_tax_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_abolish_payroll_tax()

    p = parameters(period).gov.contrib.ubi_center.flat_tax
    current_period = period_(period)

    for i in range(5):
        if p(current_period).abolish_payroll_tax:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_abolish_payroll_tax()
    else:
        return None


abolish_payroll_tax = create_abolish_payroll_tax_reform(
    None, None, bypass=True
)
