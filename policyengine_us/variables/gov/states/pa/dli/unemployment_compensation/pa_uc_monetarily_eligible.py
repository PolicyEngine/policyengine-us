from policyengine_us.model_api import *


class pa_uc_monetarily_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Monetarily eligible for Pennsylvania unemployment compensation"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=119",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        high_quarter = person("pa_uc_meets_high_quarter_test", period)
        outside_high_quarter = person(
            "pa_uc_meets_wages_outside_high_quarter_test", period
        )
        qualifying = person("pa_uc_meets_qualifying_wages_test", period)
        credit_weeks = person("pa_uc_meets_credit_weeks_test", period)
        return high_quarter & outside_high_quarter & qualifying & credit_weeks
