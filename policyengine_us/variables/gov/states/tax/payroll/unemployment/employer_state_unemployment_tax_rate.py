from policyengine_us.model_api import *


class employer_state_unemployment_tax_rate(Variable):
    value_type = float
    entity = Person
    label = "Employer state unemployment tax rate"
    documentation = (
        "Employer-side state unemployment tax rate after applying any "
        "employer-specific override."
    )
    definition_period = YEAR
    unit = "/1"

    def formula(person, period, parameters):
        override = person("employer_state_unemployment_tax_rate_override", period)
        default_rate = person("employer_state_unemployment_tax_default_rate", period)
        return where(override >= 0, override, default_rate)
