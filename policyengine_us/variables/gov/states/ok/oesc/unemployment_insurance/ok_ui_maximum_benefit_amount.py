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
        # § 2-106 caps benefits in a benefit year. Only the weeks-times-WBR
        # prong of the three-prong lesser-of test is modeled; the annual-wage
        # and wage-share caps in § 2-106 are not modeled because they depend
        # on the state-fund conditional factor that we do not track at
        # runtime.
        p = parameters(period).gov.states.ok.oesc.unemployment_insurance.mba
        weekly_benefit_rate = person("ok_ui_weekly_benefit_rate", period)
        return weekly_benefit_rate * p.max_weeks
