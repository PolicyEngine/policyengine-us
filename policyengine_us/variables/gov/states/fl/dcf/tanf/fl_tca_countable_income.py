from policyengine_us.model_api import *


class fl_tca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.210",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(12): Countable = earned after disregard + unearned
        # Unearned income has no disregard, use federal baseline directly
        countable_earned = spm_unit("fl_tca_countable_earned_income", period)
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        return countable_earned + gross_unearned
