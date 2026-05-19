from policyengine_us.model_api import *


class co_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Colorado employee state payroll tax"
    documentation = (
        "Employee-side Colorado payroll-funded contributions, including FAMLI."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO
    adds = ["co_employee_famli_contribution"]
