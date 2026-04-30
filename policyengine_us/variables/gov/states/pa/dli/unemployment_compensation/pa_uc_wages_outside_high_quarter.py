from policyengine_us.model_api import *


class pa_uc_wages_outside_high_quarter(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation wages outside the high quarter"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=119",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        base_year_wages = person("pa_uc_base_year_wages", period)
        highest_quarter_wages = person("pa_uc_highest_quarter_wages", period)
        return max_(base_year_wages - highest_quarter_wages, 0)
