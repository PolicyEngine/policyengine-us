from policyengine_us.model_api import *


class household_tax(Variable):
    value_type = float
    entity = Household
    label = "tax"
    documentation = "Total tax liability."
    unit = USD
    definition_period = YEAR
    adds = [
        "employee_payroll_tax",
        "self_employment_tax",
        "income_tax_before_refundable_credits",
        "state_income_tax",
        "flat_tax",
    ]
