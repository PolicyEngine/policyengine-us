from policyengine_us.model_api import *


class or_employee_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Oregon employee state payroll tax"
    documentation = (
        "Employee-side Oregon payroll-funded contributions, including Paid "
        "Leave and the statewide transit tax."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR
    adds = [
        "or_employee_paid_leave_contribution",
        "or_employee_statewide_transit_tax",
    ]
