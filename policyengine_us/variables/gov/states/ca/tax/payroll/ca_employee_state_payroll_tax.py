from policyengine_us.model_api import *


class ca_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "California employee state payroll tax"
    documentation = (
        "Employee-side California payroll-funded contributions, including "
        "state disability insurance withholding."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    adds = ["ca_employee_state_disability_insurance_contribution"]
