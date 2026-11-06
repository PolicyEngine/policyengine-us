from policyengine_us.model_api import *


class md_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Maryland employer additional state payroll tax"
    documentation = (
        "Employer-side Maryland Family and Medical Leave Insurance contributions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD
    adds = ["md_employer_famli_contribution"]
