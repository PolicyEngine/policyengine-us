from policyengine_us.model_api import *


class or_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Oregon employer additional state payroll tax"
    documentation = "Employer-side Oregon paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR
    adds = ["or_employer_paid_leave_contribution"]
