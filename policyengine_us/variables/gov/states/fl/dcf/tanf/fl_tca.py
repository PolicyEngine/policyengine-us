from policyengine_us.model_api import *


class fl_tca(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida Temporary Cash Assistance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.220",
    )
    defined_for = "fl_tca_eligible"

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(12) and FAC 65A-4.220
        p = parameters(period).gov.states.fl.dcf.tanf
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        countable_income = spm_unit("fl_tca_countable_income", period)

        # Benefit = Payment Standard - Countable Income
        benefit = max_(payment_standard - countable_income, 0)

        # Per FAC 65A-4.220: Minimum grant is $10; less than $10 = no payment
        return where(benefit >= p.minimum_grant, benefit, 0)
