from policyengine_us.model_api import *


class ct_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Connecticut employee state payroll tax"
    documentation = "Employee-side Connecticut payroll-funded contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CT
    adds = ["ct_employee_paid_leave_contribution"]
