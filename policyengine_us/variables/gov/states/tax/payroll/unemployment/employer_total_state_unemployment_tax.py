from policyengine_us.model_api import *


class employer_total_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total state unemployment tax"
    documentation = (
        "Employer-level state unemployment tax liability from aggregate taxable "
        "earnings inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = person("employer_state_unemployment_tax_rate", period)
        taxable_earnings = person(
            "employer_total_taxable_earnings_for_state_unemployment_tax", period
        )
        return rate * taxable_earnings
