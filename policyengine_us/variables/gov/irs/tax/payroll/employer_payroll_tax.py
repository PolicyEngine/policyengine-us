from policyengine_us.model_api import *

EMPLOYER_PAYROLL_TAX_COMPONENTS = [
    "employer_social_security_tax",
    "employer_medicare_tax",
    "employer_federal_unemployment_tax",
    "employer_state_payroll_tax",
    "employer_local_payroll_tax",
]


class employer_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer payroll tax"
    documentation = (
        "Employer-side payroll tax liability, including Social Security, "
        "Medicare, federal unemployment tax, and state and local payroll taxes."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, EMPLOYER_PAYROLL_TAX_COMPONENTS)
