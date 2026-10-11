from policyengine_us.model_api import *


class nj_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee state payroll tax"
    documentation = (
        "Employee-side New Jersey payroll-funded contributions, including "
        "temporary disability insurance, family leave insurance, unemployment "
        "insurance, and workforce development contributions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    adds = [
        "nj_employee_temporary_disability_insurance_contribution",
        "nj_employee_family_leave_insurance_contribution",
        "nj_employee_unemployment_insurance_contribution",
        "nj_employee_workforce_fund_contribution",
    ]
