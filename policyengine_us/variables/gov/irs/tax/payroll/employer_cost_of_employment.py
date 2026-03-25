from policyengine_us.model_api import *


class employer_cost_of_employment(Variable):
    value_type = float
    entity = Person
    label = "Employer cost of employment"
    documentation = (
        "Gross payroll-tax wages plus employer-side payroll taxes. Does not "
        "include benefits such as health insurance."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return person("payroll_tax_gross_wages", period) + person(
            "employer_payroll_tax", period
        )
