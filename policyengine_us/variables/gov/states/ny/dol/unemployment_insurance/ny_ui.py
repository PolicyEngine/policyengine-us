from policyengine_us.model_api import *


class ny_ui(Variable):
    value_type = float
    entity = Person
    label = "New York Unemployment Insurance"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        weekly_payable = person("ny_ui_weekly_payable", period)
        weeks_unemployed = person("ny_ui_weeks_unemployed", period)

        # Maximum benefit amount caps total benefits at the weekly rate times
        # the maximum benefit weeks within the benefit year (§ 590).
        maximum_benefit_amount = weekly_benefit_rate * p.max_weeks
        annual_benefit = weekly_payable * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
