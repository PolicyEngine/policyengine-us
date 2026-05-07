from policyengine_us.model_api import *


class pa_uc_meets_wages_outside_high_quarter_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets Pennsylvania unemployment compensation wages outside the high quarter test"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=119",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        base_year_wages = person("pa_uc_base_year_wages", period)
        wages_outside_high_quarter = person("pa_uc_wages_outside_high_quarter", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        required = base_year_wages * p.wages_outside_high_quarter_fraction
        return wages_outside_high_quarter >= required
