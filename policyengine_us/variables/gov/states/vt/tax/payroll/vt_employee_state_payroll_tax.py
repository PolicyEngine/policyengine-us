from policyengine_us.model_api import *


class vt_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Vermont employee state payroll tax"
    documentation = "Employee-side Vermont child care contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT
    adds = ["vt_employee_child_care_contribution"]
