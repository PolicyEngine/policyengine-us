from policyengine_us.model_api import *


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
        "flat_tax",
        "household_state_tax_before_refundable_credits",
    ]
