from policyengine_us.model_api import *

EMPLOYER_TOTAL_PAYROLL_TAX_COMPONENTS = [
    "employer_total_social_security_tax",
    "employer_total_medicare_tax",
    "employer_total_federal_unemployment_tax",
    "employer_total_state_payroll_tax",
    "employer_total_local_payroll_tax",
]


class employer_total_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total payroll tax"
    documentation = (
        "Employer-level payroll tax liability from aggregate employer inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, EMPLOYER_TOTAL_PAYROLL_TAX_COMPONENTS)
