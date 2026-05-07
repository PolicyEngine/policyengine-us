from policyengine_us.model_api import *


class pa_uc_meets_qualifying_wages_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Pennsylvania unemployment compensation qualifying wages test"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        base_year_wages = person("pa_uc_base_year_wages", period)
        qualifying_wages = person("pa_uc_qualifying_wages", period)
        return base_year_wages >= qualifying_wages
