from policyengine_us.model_api import *


class ny_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "New York pension exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.law.cornell.edu/regulations/new-york/20-NYCRR-112.3"

    def formula(person, period, parameters):
        # Fetching values from separate YAML files
        p = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion

        pension_income = add(person, period, p.sources)
        age = person("age", period)
        meets_age_test = age >= p.min_age

        return meets_age_test * min_(pension_income, p.cap)
