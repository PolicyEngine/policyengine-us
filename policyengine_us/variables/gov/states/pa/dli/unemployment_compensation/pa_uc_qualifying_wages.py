from policyengine_us.model_api import *


class pa_uc_qualifying_wages(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation qualifying wages"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=132",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        highest_quarter_wages = person("pa_uc_highest_quarter_wages", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        return p.qualifying_wages.calc(highest_quarter_wages)
