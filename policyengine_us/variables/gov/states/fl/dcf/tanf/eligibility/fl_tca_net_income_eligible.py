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
        # Per DCF 2620.0107, total net income "cannot exceed" the appropriate
        # income limit (the payment standard), and 2620.0111.01 Step 5 makes the
        # AG ineligible only "if a surplus results." An exact equal produces no
        # surplus (2620.0109.02 Step 2: "Deficit or Exact Equal: Meets the
        # Requirements"), so countable income exactly at the payment standard is
        # eligible. The boundary is <=, not strict <.
        countable_income = spm_unit("fl_tca_countable_income", period)
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        return countable_income <= payment_standard
