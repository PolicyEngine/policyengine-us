from policyengine_us.model_api import *


class ny_ui_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "NY UI weekly benefit rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        raw_weekly_benefit_rate = person("ny_ui_raw_weekly_benefit_rate", period)
        return min_(max_(raw_weekly_benefit_rate, p.min_amount), p.max_amount)
