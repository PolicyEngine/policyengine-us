from policyengine_us.model_api import *


class employer_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer state payroll tax"
    documentation = (
        "Employer-side state payroll tax liability, including unemployment "
        "insurance and other state payroll-funded contributions."
    )
    definition_period = YEAR
    unit = USD
    adds = [
        "employer_state_unemployment_tax",
        "employer_additional_state_payroll_tax",
    ]
