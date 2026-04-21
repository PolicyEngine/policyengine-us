from policyengine_us.model_api import *


class pa_uc_meets_high_quarter_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Pennsylvania unemployment compensation high quarter wages test"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=132",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        highest_quarter_wages = person("pa_uc_highest_quarter_wages", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        return highest_quarter_wages >= p.minimum_high_quarter_wages
