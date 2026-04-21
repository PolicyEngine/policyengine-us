from policyengine_us.model_api import *


class pa_uc_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation weekly benefit rate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=136",
        "https://www.pacodeandbulletin.gov/Display/pabull?file=/secure/pabulletin/data/vol54/54-52/1863.html",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        highest_quarter_wages = person("pa_uc_highest_quarter_wages", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        return p.rate_table.calc(highest_quarter_wages)
