from policyengine_us.model_api import *


class ri_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island employer additional state payroll tax"
    documentation = "Employer-side Rhode Island payroll contributions beyond UI."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI
    adds = ["ri_employer_job_development_fund_tax"]
