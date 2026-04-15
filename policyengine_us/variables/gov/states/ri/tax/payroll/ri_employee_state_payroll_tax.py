from policyengine_us.model_api import *


class ri_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island employee state payroll tax"
    documentation = (
        "Employee-side Rhode Island payroll-funded contributions, including TDI."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI
    adds = ["ri_employee_temporary_disability_insurance_contribution"]
