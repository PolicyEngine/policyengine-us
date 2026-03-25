from policyengine_us.model_api import *


class ca_employer_employment_training_tax(Variable):
    value_type = float
    entity = Person
    label = "California employer employment training tax"
    documentation = "Employer-side California Employment Training Tax liability."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        rate = parameters(
            period
        ).gov.states.ca.tax.payroll.employment_training.employer_rate
        return rate * person("taxable_earnings_for_state_unemployment_tax", period)
