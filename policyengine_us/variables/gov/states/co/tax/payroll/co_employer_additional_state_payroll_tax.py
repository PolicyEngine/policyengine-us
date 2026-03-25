from policyengine_us.model_api import *


class co_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Colorado employer additional state payroll tax"
    documentation = "Colorado employer payroll-funded contributions beyond UI."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO
    adds = ["co_employer_famli_contribution"]
