from policyengine_us.model_api import *


class ak_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Alaska employee state payroll tax"
    documentation = (
        "Employee-side Alaska payroll-funded contributions, including "
        "unemployment insurance."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.AK
    adds = ["ak_employee_unemployment_insurance_contribution"]
