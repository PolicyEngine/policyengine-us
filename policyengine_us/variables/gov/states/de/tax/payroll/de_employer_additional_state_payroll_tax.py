from policyengine_us.model_api import *


class de_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Delaware employer additional state payroll tax"
    documentation = "Employer-side Delaware paid leave contributions."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DE
    adds = ["de_employer_paid_leave_contribution"]
