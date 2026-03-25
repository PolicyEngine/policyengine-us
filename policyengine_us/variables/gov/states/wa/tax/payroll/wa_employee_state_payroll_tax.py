from policyengine_us.model_api import *


class wa_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Washington employee state payroll tax"
    documentation = (
        "Employee-side Washington payroll-funded contributions, including Paid "
        "Leave and WA Cares."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    adds = [
        "wa_employee_paid_leave_contribution",
        "wa_employee_long_term_care_contribution",
    ]
