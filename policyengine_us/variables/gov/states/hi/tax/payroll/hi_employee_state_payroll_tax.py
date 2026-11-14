from policyengine_us.model_api import *


class hi_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Hawaii employee state payroll tax"
    documentation = (
        "Employee-side Hawaii payroll-funded contributions. Hawaii's temporary "
        "disability insurance contribution goes to the employer's plan or "
        "insurer, not to the State."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    adds = ["hi_employee_temporary_disability_insurance_contribution"]
