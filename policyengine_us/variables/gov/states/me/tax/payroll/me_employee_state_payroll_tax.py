from policyengine_us.model_api import *


class me_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Maine employee state payroll tax"
    documentation = "Employee-side Maine paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME
    adds = ["me_employee_paid_leave_contribution"]
