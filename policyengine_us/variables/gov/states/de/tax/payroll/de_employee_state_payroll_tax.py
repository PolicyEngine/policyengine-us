from policyengine_us.model_api import *


class de_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Delaware employee state payroll tax"
    documentation = "Employee-side Delaware paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE
    adds = ["de_employee_paid_leave_contribution"]
