from policyengine_us.model_api import *


class ok_ui_maximum_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma UI maximum benefit amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=48",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=51",
    )

    def formula(person, period, parameters):
        # § 2-106 caps benefits in a benefit year at the lesser of the
        # duration cap, the statewide maximum benefit amount, and the
        # applicable share of base-period wages.
        p = parameters(period).gov.states.ok.oesc.unemployment_insurance.mba
        weekly_benefit_rate = person("ok_ui_weekly_benefit_rate", period)
        base_period_total_wages = person("ok_ui_base_period_total_wages", period)
        return min_(
            min_(weekly_benefit_rate * p.max_weeks, p.max_amount),
            base_period_total_wages * p.base_period_wages_share,
        )
