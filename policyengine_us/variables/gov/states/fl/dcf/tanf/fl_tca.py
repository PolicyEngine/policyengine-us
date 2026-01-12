from policyengine_us.model_api import *


class fl_tca(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida Temporary Cash Assistance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-65A-4-220",
    )
    defined_for = "fl_tca_eligible"

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(12) and FAC 65A-4.220
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        countable_income = spm_unit("fl_tca_countable_income", period)

        # Benefit = Payment Standard - Countable Income
        return max_(payment_standard - countable_income, 0)
