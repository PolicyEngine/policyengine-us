from policyengine_us.model_api import *


class dc_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "District of Columbia employer additional state payroll tax"
    documentation = "District employer payroll-funded contributions beyond UI."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC
    adds = ["dc_employer_paid_leave_tax"]
