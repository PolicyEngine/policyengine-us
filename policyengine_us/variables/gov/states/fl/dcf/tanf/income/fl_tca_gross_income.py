from policyengine_us.model_api import *


class fl_tca_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html"
    defined_for = StateCode.FL

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
