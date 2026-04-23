from policyengine_us.model_api import *


class me_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Maine employer additional state payroll tax"
    documentation = "Employer-side Maine paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.ME
    adds = ["me_employer_paid_leave_contribution"]
