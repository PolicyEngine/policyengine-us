from policyengine_us.model_api import *


class pa_uc_meets_credit_weeks_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Pennsylvania unemployment compensation credit weeks test"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        credit_weeks = person("pa_uc_credit_weeks", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        return credit_weeks >= p.minimum_credit_weeks
