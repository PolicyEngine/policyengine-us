from policyengine_us.model_api import *


class employer_total_cost_of_employment(Variable):
    value_type = float
    entity = Person
    label = "Employer total cost of employment"
    documentation = (
        "Aggregate payroll-tax wages plus employer-level payroll taxes from "
        "employer input data."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return person("employer_total_payroll_tax_gross_wages", period) + person(
            "employer_total_payroll_tax", period
        )
