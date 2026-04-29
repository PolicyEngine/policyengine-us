from policyengine_us.model_api import *


class employer_total_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total state payroll tax"
    documentation = (
        "Employer-level state payroll tax liability from aggregate employer inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return person("employer_total_state_unemployment_tax", period) + person(
            "employer_total_additional_state_payroll_tax", period
        )
