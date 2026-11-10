from policyengine_us.model_api import *


class mn_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Minnesota employer additional state payroll tax"
    documentation = "Employer-side Minnesota Paid Leave premium."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MN
    adds = ["mn_employer_paid_leave_contribution"]
