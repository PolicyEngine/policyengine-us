from policyengine_us.model_api import *


class pa_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania employee state payroll tax"
    documentation = (
        "Employee-side Pennsylvania payroll-funded contributions, including "
        "unemployment compensation withholding."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.PA
    adds = ["pa_employee_unemployment_compensation_contribution"]
