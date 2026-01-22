from policyengine_us.model_api import *


class fl_tca_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA net income eligible"
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-65A-4-220",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(12): Net countable income < payment standard
        countable_income = spm_unit("fl_tca_countable_income", period)
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        return countable_income < payment_standard
