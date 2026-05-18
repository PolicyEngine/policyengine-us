from policyengine_us.model_api import *


class ny_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "New York employee state payroll tax"
    documentation = (
        "Employee-side New York payroll-funded contributions, including Paid "
        "Family Leave and Disability Benefits withholding."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    adds = [
        "ny_employee_paid_family_leave_contribution",
        "ny_employee_disability_benefits_contribution",
    ]
