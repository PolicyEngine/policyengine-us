from policyengine_us.model_api import *


class ca_employer_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "California employer state unemployment tax"
    documentation = "Employer-side unemployment tax liability for California."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return person("employer_state_unemployment_tax_rate", period) * person(
            "taxable_earnings_for_state_unemployment_tax", period
        )
