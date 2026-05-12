from policyengine_us.model_api import *


class ok_ui_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma UI weekly payable amount"
    unit = USD
    definition_period = YEAR
    defined_for = "ok_ui_monetarily_eligible"
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=50",
    )

    def formula(person, period, parameters):
        # § 2-105: weekly payable amount = WBR minus the portion of weekly
        # earnings that exceeds the statutory earnings disregard, floored at
        # zero.
        p = parameters(period).gov.states.ok.oesc.unemployment_insurance.partial
        weekly_benefit_rate = person("ok_ui_weekly_benefit_rate", period)
        gross_weekly_earnings = person("ok_ui_gross_weekly_earnings", period)
        earnings_reduction = max_(gross_weekly_earnings - p.disregard, 0)
        return max_(weekly_benefit_rate - earnings_reduction, 0)
