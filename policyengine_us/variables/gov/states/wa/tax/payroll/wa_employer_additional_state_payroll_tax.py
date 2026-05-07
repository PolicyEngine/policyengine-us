from policyengine_us.model_api import *


class wa_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Washington employer additional state payroll tax"
    documentation = "Employer-side Washington paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    adds = ["wa_employer_paid_leave_contribution"]
