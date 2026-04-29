from policyengine_us.model_api import *


class ma_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer additional state payroll tax"
    documentation = "Employer-side Massachusetts PFML contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA
    adds = ["ma_employer_paid_leave_contribution"]
