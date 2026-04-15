from policyengine_us.model_api import *


class ma_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employee state payroll tax"
    documentation = "Employee-side Massachusetts PFML contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA
    adds = ["ma_employee_paid_leave_contribution"]
