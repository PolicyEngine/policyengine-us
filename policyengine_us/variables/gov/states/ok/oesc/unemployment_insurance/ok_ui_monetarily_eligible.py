from policyengine_us.model_api import *


class ok_ui_monetarily_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Monetarily eligible for Oklahoma Unemployment Insurance"
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=56",
    )

    def formula(person, period, parameters):
        high_quarter = person("ok_ui_meets_high_quarter_test", period)
        alternate = person("ok_ui_meets_alternate_wages_test", period)
        return high_quarter | alternate
