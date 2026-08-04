from policyengine_us.model_api import *


class ny_ui(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    defined_for = "ny_ui_monetarily_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        weekly_payable = person("ny_ui_weekly_payable", period)
        # Floor weeks at zero so a negative input cannot produce a negative
        # benefit (mirrors the AL/OK UI guard pattern).
        weeks_unemployed = max_(person("weeks_unemployed", period), 0)

        # Maximum benefit amount caps total benefits at the weekly rate times
        # the maximum benefit weeks within the benefit year (§ 590).
        maximum_benefit_amount = weekly_benefit_rate * p.max_weeks
        annual_benefit = weekly_payable * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
