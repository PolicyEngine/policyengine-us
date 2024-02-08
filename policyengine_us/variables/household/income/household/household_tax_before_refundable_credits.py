from policyengine_us.model_api import *


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
        flat_tax = p.gov.contrib.ubi_center.flat_tax
        if p.simulation.reported_state_income_tax:
            added_components = [
                "employee_payroll_tax",
                "self_employment_tax",
                "income_tax_before_refundable_credits",  # Federal.
                "flat_tax",
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
