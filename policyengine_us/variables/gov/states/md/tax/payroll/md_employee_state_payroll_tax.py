from policyengine_us.model_api import *


class md_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Maryland employee state payroll tax"
    documentation = (
        "Employee-side Maryland Family and Medical Leave Insurance contributions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD
    adds = ["md_employee_famli_contribution"]
