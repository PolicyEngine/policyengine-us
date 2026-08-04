from policyengine_us.model_api import *


class mn_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Minnesota employee state payroll tax"
    documentation = "Employee-side Minnesota Paid Leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    adds = ["mn_employee_paid_leave_contribution"]
