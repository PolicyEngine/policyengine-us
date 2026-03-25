from policyengine_us.model_api import *


class vt_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Vermont employer additional state payroll tax"
    documentation = "Employer-side Vermont child care contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT
    adds = ["vt_employer_child_care_contribution"]
