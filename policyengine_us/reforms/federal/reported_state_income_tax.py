from policyengine_us.model_api import *


def create_reported_state_income_tax() -> Reform:
    class household_tax_before_refundable_credits(Variable):
        value_type = float
        entity = Household
        label = "total tax before refundable credits"
        documentation = "Total tax liability before refundable credits."
        unit = USD
        definition_period = YEAR

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = p.gov.household_tax_before_refundable_credits
            added_components = [
                "employee_payroll_tax",
                "self_employment_tax",
                "income_tax_before_refundable_credits",  # Federal.
                "flat_tax",
                # State tax reported in ASEC includes refundable credits.
                "spm_unit_state_tax_reported",
            ]
            return add(household, period, added_components)

    class household_refundable_tax_credits(Variable):
        value_type = float
        entity = Household
        label = "refundable tax credits"
        definition_period = YEAR
        unit = USD

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = p.gov.household_refundable_credits
            # State tax reported in ASEC includes refundable credits.
            # So we get refundable credits in household_tax_before_refundable_credits
            # via spm_unit_state_tax_reported.
            added_components = [
                "income_tax_refundable_credits",  # Federal.
            ]
            return add(household, period, added_components)

    class reform(Reform):
        def apply(self):
            self.update_variable(household_tax_before_refundable_credits)
            self.update_variable(household_refundable_tax_credits)

    return reform


def create_reported_state_income_tax_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reported_state_income_tax()

    p = parameters(period).simulation

    if p.reported_state_income_tax == True:
        return create_reported_state_income_tax()
    else:
        return None


reported_state_income_tax = create_reported_state_income_tax_reform(
    None, None, bypass=True
)
