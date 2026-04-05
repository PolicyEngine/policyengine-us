from policyengine_us.model_api import *


class ca_employer_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "California employer additional state payroll tax"
    documentation = (
        "California employer payroll-funded contributions other than "
        "unemployment insurance."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    adds = ["ca_employer_employment_training_tax"]
