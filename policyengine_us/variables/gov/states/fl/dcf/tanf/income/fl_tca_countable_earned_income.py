from policyengine_us.model_api import *


class fl_tca_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=27",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=28",
        "https://ffic.myflfamilies.com/manual/2600.pdf#page=21",
    )
    defined_for = StateCode.FL

    # Per DCF 2420.0304 and 2420.0314, the $90 standard disregard and the
    # $200 and 1/2 disregard apply to each individual's earned income.
    adds = ["fl_tca_countable_earned_income_person"]
