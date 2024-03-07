from policyengine_us.model_api import *


def create_reported_state_income_tax() -> Reform:
    class household_tax_before_refundable_credits(Variable):
        value_type = float
        entity = Household
        label = "total tax before refundable credits"
        documentation = "Total tax liability before refundable credits."
        unit = USD
        definition_period = YEAR

        adds = [
            "employee_payroll_tax",
            "self_employment_tax",
            "income_tax_before_refundable_credits",
            "spm_unit_state_tax_reported",
            "flat_tax",
        ]

        def formula(household, period, parameters):
            p = parameters(period)
            added_components = p.gov.household_tax_before_refundable_credits
            flat_tax = p.gov.contrib.ubi_center.flat_tax
            if p.simulation.reported_state_income_tax:
                added_components = [
                    "employee_payroll_tax",
                    "self_employment_tax",
                    "income_tax_before_refundable_credits",  # Federal.
                    "flat_tax",
                    # State tax reported in ASEC includes refundable credits.
                    "spm_unit_state_tax_reported",
                ]
            if flat_tax.abolish_payroll_tax:
                added_components = [
                    c for c in added_components if c != "employee_payroll_tax"
                ]
            if flat_tax.abolish_federal_income_tax:
                added_components = [
                    c
                    for c in added_components
                    if c != "income_tax_before_refundable_credits"
                ]
            return add(household, period, added_components)

    class household_refundable_tax_credits(Variable):
        value_type = float
        entity = Household
        label = "refundable tax credits"
        definition_period = YEAR
        unit = USD

        adds = ["income_tax_refundable_credits"]

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

    if p.reported_state_income_tax:
        return create_reported_state_income_tax()
    else:
        return None


reported_state_income_tax = create_reported_state_income_tax_reform(
    None, None, bypass=True
)
